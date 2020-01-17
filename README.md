# h2o_rest_api
Rest API that server a Machine Learning model made wirh H2o ai

## DATA _The data comes from dataset: 
Kaggle’s Can You Predict Product Backorders? _ The data file contains the historical data for the 8 weeks prior to the week we are trying to predict. The data were taken as weekly snapshots at the start of each week. The target (or response) is the went_on_backorder variable. To model and predict the target, we’ll use the other features, which include:

sku – Random ID for the product  
national_inv – Current inventory level for the part  
lead_time – Transit time for product (if available)  
in_transit_qty – Amount of product in transit from source  
forecast_3_month – Forecast sales for the next 3 months  
forecast_6_month – Forecast sales for the next 6 months  
forecast_9_month – Forecast sales for the next 9 months  
sales_1_month – Sales quantity for the prior 1 month time period  
sales_3_month – Sales quantity for the prior 3 month time period  
sales_6_month – Sales quantity for the prior 6 month time period  
sales_9_month – Sales quantity for the prior 9 month time period  
min_bank – Minimum recommend amount to stock  
potential_issue – Source issue for part identified  
pieces_past_due – Parts overdue from source  
perf_6_month_avg – Source performance for prior 6 month period  
perf_12_month_avg – Source performance for prior 12 month period  
local_bo_qty – Amount of stock orders overdue  
deck_risk – Part risk flag  
oe_constraint – Part risk flag  
ppap_risk – Part risk flag  
stop_auto_buy – Part risk flag  
rev_stop – Part risk flag  
went_on_backorder – Product actually went on backorder. This is the target value.  

# API Behavior
You can access Swagger through root directory ("/"). The api has two endpoints:
* ('/train'): Which will train a new model and serve it. So far, the train endpoint does not allow new datasets.
* ('/test'): Test the set of parameters providades as a json and return if the product will go on backorder. For more information about the parameter check the Swagger documentation
