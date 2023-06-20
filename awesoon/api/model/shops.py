from flask_restx import fields


shop = {
    "name": fields.String(required=True),
    "shop_identifier": fields.Integer(required=True),
    "shop_url": fields.String(required=True),
}


shopify_app = {
    "name": fields.String(required=True),
    "app_client_id": fields.String(required=True),
    "app_client_secret": fields.String(required=True)
}

shopify_installation = {
    "name": fields.String(required=True),
    "app_client_id": fields.String(required=True),
    "app_client_secret": fields.String(required=True)
}
