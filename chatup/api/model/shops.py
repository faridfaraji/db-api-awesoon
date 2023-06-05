from flask_restx import fields

shop = {
    "name": fields.String(required=True),
    "shop_id": fields.Integer(required=True),
    "shop_url": fields.String(required=True),
    "access_token": fields.String(required=True),
    "description": fields.String(required=False, default="")
}
