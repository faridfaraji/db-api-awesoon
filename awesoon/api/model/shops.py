from flask_restx import fields

shop = {
    "shop_name": fields.String(required=True),
    "shop_identifier": fields.Integer(required=True),
    "shop_url": fields.String(required=True),
    "contact_email": fields.String(required=True),
    "conversations_count": fields.Integer(readonly=True),
    "message_counts": fields.Integer(readonly=True),
    "latest_scan_id": fields.String(required=True),
    "bot_temperature": fields.Float(required=True, default=0),
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
    "shop_url": fields.String(required=True)
}


def add_shop_parser(parser):
    parser.add_argument("shop_name", type=str, default=None, location="json")
    parser.add_argument("shop_url", type=str, default=None, location="json")
    parser.add_argument("contact_email", type=str, default=None, location="json")
    parser.add_argument(
        "bot_temperature", help="Bot temperature must be a float between 0 and 2",
        type=float, default=0, location="json"
    )
