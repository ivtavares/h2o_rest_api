import h2o
from h2o.automl import H2OAutoML
import os
import json


def connect_to_server():
    try:
        h2o.init(url='http://54.166.48.156:54321/',
             username=os.environ.get('username'),
             password=os.environ.get('password'))
        return 200
    except Exception as e:
        return 500


def load_json(file_path):
    with open(file_path) as json_file:
        return json.load(json_file)


# Start automl
server_status = connect_to_server()
parameters_path = 'app/parameters/'
features = load_json(parameters_path+'features.json')['automl']
model_path = load_json(parameters_path+'predict.json')['model_path']


def train(dataset_url, dataset_features = features):
    df = h2o.import_file(dataset_url)

    # Split values
    df_train, df_test = df.split_frame(ratios=[0.8], seed=1)

    # Set fields to test
    y_name = 'went_on_backorder'
    X_columns = df.columns
    X_columns.remove(y_name)
    X_columns.remove('sku')

    if set(X_columns) != set(dataset_features):
        print('Wrong dataset')
        return 'teste'

    # Train the model
    aml = H2OAutoML(seed=1, max_runtime_secs=30)
    aml.train(x=X_columns, y=y_name, training_frame=df_train)

    # Perform accuracy test
    perf = aml.leader.model_performance(df_test)
    accuracy = perf.auc()

    # Save model
    path = h2o.save_model(model=aml.leader, path="/tmp/mymodel", force=True)

    # Save new path
    file_json = {'model_path': path}
    os.remove(parameters_path+'predict.json')
    with open(parameters_path+'predict.json', 'w') as f:
        json.dump(file_json, f)

    # return parameters
    return path, accuracy


#train first model
try:
    aml_model = h2o.load_model(model_path)
except:
    model_path, accuracy = train("https://h2obucketest.s3-sa-east-1.amazonaws.com/Kaggle_Training_Dataset_v2.csv", features)
    print('model path: {}, accuracy: {}'.format(model_path, accuracy))
    aml_model = h2o.load_model(model_path)


def predict(dataset, model=aml_model):
    # Predict on a h20 frame and return JSON response.
    h2o_test_frame = h2o.H2OFrame(dataset)
    estimate = model.predict(h2o_test_frame)[0].as_data_frame(use_pandas=False, header=False)[0][0]
    response = dict(WILL_GO_ON_BACKORDER=estimate)
    return response

