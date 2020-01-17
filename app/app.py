# Packages to import
from flask import Flask, jsonify, request
from flask_restplus import Api, Resource, fields
import json
import os
import h2o
from h2o.automl import H2OAutoML


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


def load_parameters():
    with open('app/parameters/predict.json') as json_file:
        parameters = json.load(json_file)
        return parameters['features'], parameters['model_path']


def connect_to_server():
    username = os.environ.get('username')
    password = os.environ.get('password')
    try:
        h2o.init(url='http://3.92.211.117:54321/',
             username=username,
             password=password)
        return 200
    except Exception as e:
        return 500

def train(dataset_url):
    df = h2o.import_file(dataset_url)

    # Split values
    df_train, df_test = df.split_frame(ratios=[0.8], seed=1)

    # Set fields to test
    y_name = 'went_on_backorder'
    X_columns = df.columns
    X_columns.remove(y_name)
    X_columns.remove('sku')

    # Train the model
    aml = H2OAutoML(seed=1, max_runtime_secs=30)
    aml.train(x=X_columns, y=y_name, training_frame=df_train)

    # Perform accuracy test
    perf = aml.leader.model_performance(df_test)
    accuracy = perf.auc()

    # Save model
    path = h2o.save_model(model=aml.leader, path="/tmp/mymodel", force=True)

    # Save new path
    file_json = {'features': features,
                 'model_path': path}
    os.remove('app/parameters/predict.json')
    with open('app/parameters/predict.json', 'w') as f:
        json.dump(file_json, f)

    # return parameters
    return dict(MODEL_PATH=path, ACCURACY=accuracy)


# Initialize de api
app = Flask(__name__)
api = Api(app=app, title="ML model serving", description="Create rest microservice to serve an ML Model")
name_space = api.namespace('ML Model', description='API ML')

status = connect_to_server()

try:
    features, model_path = load_parameters()
    aml_model = h2o.load_model(model_path)
except:
    model_information = train("https://h2obucketest.s3-sa-east-1.amazonaws.com/Kaggle_Training_Dataset_v2.csv")
    features, model_path = load_parameters()
    aml_model = h2o.load_model(model_path)


features_model = api.model('Features', {
    "national_inv":  fields.Integer(required=True, description='Current inventory level for the part'),
    "lead_time": fields.Integer(required=True, description='Transit time for product'),
    "in_transit_qty":  fields.Integer(required=True, description='Amount of product in transit from source'),
    "forecast_3_month": fields.Integer(required=True, description='Forecast sales for the next 3 months'),
    "forecast_6_month": fields.Integer(required=True, description='Forecast sales for the next 6 months'),
    "forecast_9_month": fields.Integer(required=True, description='Forecast sales for the next 9 months'),
    "sales_1_month": fields.Integer(required=True, description='Sales quantity for the prior 1 month time period'),
    "sales_3_month": fields.Integer(required=True, description='Sales quantity for the prior 3 month time period'),
    "sales_6_month": fields.Integer(required=True, description='Sales quantity for the prior 6 month time period'),
    "sales_9_month": fields.Integer(required=True, description='Sales quantity for the prior 9 month time period'),
    "min_bank": fields.Integer(required=True, description='Minimum recommend amount to stock'),
    "potential_issue": fields.String(required=True, description='Source issue for part identified'),
    "pieces_past_due": fields.Integer(required=True, description='Parts overdue from source'),
    "perf_6_month_avg": fields.Integer(required=True, description='Source performance for prior 6 month period'),
    "perf_12_month_avg": fields.Integer(required=True, description='Source performance for prior 12 month period'),
    "local_bo_qty": fields.Integer(required=True, description='Amount of stock orders overdue'),
    "deck_risk": fields.String(required=True, description='Part risk flag'),
    "oe_constraint": fields.String(required=True, description='Part risk flag'),
    "ppap_risk": fields.String(required=True, description='Part risk flag'),
    "stop_auto_buy": fields.String(required=True, description='Part risk flag'),
    "rev_stop": fields.String(required=True, description='Part risk flag')
})


@app.before_request
def check_status():
    global status
    if status == 500:
        raise InvalidUsage('Could not connect to ther H20 IA Server', status_code=500)


@api.route('/predict', methods=['POST'])
class Predict(Resource):
    @api.expect(features_model)
    @api.response(200, 'Value predicted.')
    @api.response(400, 'Could not predict the value.')
    def post(self):
        """Handle request and return prediction in json format."""
        # Handle empty requests.
        if not request.json:
            raise InvalidUsage('No request received')
        elif set(request.json.keys()) != set(features):
            raise InvalidUsage('Wrong features', status_code=418)

        X_list = request.json
        h2o_test_frame = h2o.H2OFrame(X_list)

        # Predict on a h20 frame and return JSON response.
        try:
            estimate = aml_model.predict(h2o_test_frame)[0].as_data_frame(use_pandas=False, header=False)[0][0]
            response = dict(WILL_GO_ON_BACKORDER=estimate)
            return jsonify(response)
        except Exception as e:
            raise InvalidUsage('Could not predict the value')


@api.route('/train')
class Train(Resource):
    @api.response(200, 'Model trained.')
    def get(self):
        """Train the model"""
        # Load Dataframe
        response = train("https://h2obucketest.s3-sa-east-1.amazonaws.com/Kaggle_Training_Dataset_v2.csv")

        # Return model result
        return jsonify(response)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


if __name__ == '__main__':
    app.run()
