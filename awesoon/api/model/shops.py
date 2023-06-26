from flask_restx import fields

shop = {
    "shop_name": fields.String(required=True),
    "shop_identifier": fields.Integer(required=True),
    "shop_url": fields.String(required=True),
    "contact_email": fields.String(required=True)
}


shopify_app = {
    "app_name": fields.String(required=True),
    "app_client_id": fields.String(required=True),
    "app_client_secret": fields.String(required=True),
}

shopify_installation = {
    "id": fields.String(readonly=True),
    "app_name": fields.String(required=True),
    "access_token": fields.String(required=True),
    "shop_url": fields.String(required=True),
}


def add_shop_parser(parser):
    parser.add_argument("shop_name", type=str, default=None, location="json")
    parser.add_argument("shop_url", type=str, default=None, location="json")
    parser.add_argument("contact_email", type=str, default=None, location="json")
