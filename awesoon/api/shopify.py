import sys

from flask_restx import Namespace, Resource, marshal

from awesoon.api.model.shops import shopify_app
from awesoon.constants import SUCCESS_MESSAGE
from awesoon.core.database.shopify import get_shopify_apps
from awesoon.model.schema import Session
from awesoon.model.schema.shop import ShopifyApp as ShopifyAppSchema

api = Namespace("shopify-apps", "This namespace is responsible for adding and retrieving shopify apps")

shopify_app_model = api.model("shopify-app", shopify_app)
shopify_app_parser = api.parser()
shopify_app_parser.add_argument("app_name", type=str, default=None, location="json")
shopify_app_parser.add_argument("app_client_id", type=str, default=None, location="json")
shopify_app_parser.add_argument("app_client_secret", type=str, default=None, location="json")

get_shopify_app_parser = api.parser()
get_shopify_app_parser.add_argument("app_name", type=str, default=None, location="values")


@api.route("")
class ShopifyApp(Resource):
    @api.expect(get_shopify_app_parser)
    def get(self):
        with Session() as session:
            try:
                args = get_shopify_app_parser.parse_args()
                apps = get_shopify_apps(session, args)
                return marshal(apps, shopify_app_model), 200
            except Exception as e:
                print(e, file=sys.stderr)
                api.abort(500)

    @api.expect(shopify_app_model)
    def post(self):
        with Session() as session:
            try:
                shopify_app_data = shopify_app_parser.parse_args()
                shopify_app = ShopifyAppSchema(**shopify_app_data)
                session.add(shopify_app)
                session.commit()
                return SUCCESS_MESSAGE, 200
            except Exception as e:
                print(e, file=sys.stderr)
                api.abort(500)
