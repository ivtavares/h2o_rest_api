from flask_restplus import fields


def return_features_model(api):
    return api.model('Features', {
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
