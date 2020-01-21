# Packages to import
from flask import Flask, jsonify, request
from flask_restplus import Resource
from flask_restplus import Api
from app.utils.invalidusage import InvalidUsage
from app.utils.models import return_features_model
from app.mlmodels.automl import features, predict, train, server_status


# Initialize de api
app = Flask(__name__)
api = Api(app=app, title="ML model serving", description="Create rest microservice to serve an ML Model")
name_space = api.namespace('ML Model', description='API ML')
features_model = return_features_model(api)


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
        x_list = request.json
        try:
            return jsonify(predict(x_list))
        except Exception as e:
            raise InvalidUsage('Could not predict the value')


@api.route('/train')
class Train(Resource):
    @api.response(200, 'Model trained.')
    def get(self):
        """Train the model"""
        # Load Dataframe
        model_path, accuracy = train("https://h2obucketest.s3-sa-east-1.amazonaws.com/Kaggle_Training_Dataset_v2.csv")
        response = dict(MODEL_PATH=model_path, ACCURACY=accuracy)
        # Return model result
        return jsonify(response)


@app.before_request
def check_status():
    if server_status == 500:
        raise InvalidUsage('Could not connect to ther H20 IA Server', status_code=500)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


if __name__ == '__main__':
    app.run()
