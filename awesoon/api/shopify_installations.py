import sys

from flask_restx import Namespace, Resource

from awesoon.core.database.shopify import delete_shop_shopify_installation
from awesoon.model.schema import Session

api = Namespace(
    "shopify-installations", "This namespace is responsible for adding and retrieving shopify installations")


@api.route("/<id>")
class ShopifyAppInstallation(Resource):
    def delete(self, id):
        with Session() as session:
            try:
                delete_shop_shopify_installation(session, id)
                session.commit()
            except Exception as e:
                print(e, file=sys.stderr)
                api.abort(500)
