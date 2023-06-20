import sys

from flask_restx import Namespace, Resource

from awesoon.core.database.shopify import delete_shop_shopify_installation
from awesoon.model.schema import Session
from flask_restx import Namespace, Resource, marshal

ns = Namespace(
    "shopify-installations", "This namespace is resposible for adding and retrieving shopify installations")


@ns.route("/<id>")
class ShopifyAppInstallation(Resource):
    def delete(self, id):
        with Session() as session:
            try:
                delete_shop_shopify_installation(session, id)
                session.commit()
            except Exception as e:
                print(e, file=sys.stderr)
                ns.abort(500)
