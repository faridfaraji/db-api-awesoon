from flask_restx import fields


shop = {
    "shop_name": fields.String(required=True),
    "shop_identifier": fields.Integer(required=True),
    "shop_url": fields.String(required=True),
}


shopify_app = {
    "app_name": fields.String(required=True),
    "app_client_id": fields.String(required=True),
    "app_client_secret": fields.String(required=True),
}

shopify_installation = {
    "app_name": fields.String(required=True),
    "app_client_id": fields.String(required=True),
    "app_client_secret": fields.String(required=True),
}
