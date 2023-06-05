import sys

from flask import request
from flask_restx import Namespace, Resource
from sqlalchemy import select
from flask_restx import Namespace, Resource, marshal

from chatup.api.model.shops import shop
from chatup.core.database.shops import upsert_shop
from chatup.model.schema import Session
from chatup.model.schema.shop import Shop
ns = Namespace(
    "shops", "This namespace is resposible for retrieving and storing the shops info.")

shop_model = ns.model(
    "model",
    shop
)


shop_parser = ns.parser()
shop_parser.add_argument("name", type=str, default=None, location="json")
shop_parser.add_argument("shop_url", type=str, default=None, location="json")
shop_parser.add_argument("access_token", type=str, default=None, location="json")
shop_parser.add_argument("description", type=str, default="", location="json")


@ns.route("/")
class Shops(Resource):
    def get(self):
        with Session() as session:
            query = select(Shop)
            shops = session.scalars(query).all()
            marshalled_shops = marshal(shops, shop_model)
        return marshalled_shops, 200


@ns.route("/<id>")
class SingleShop(Resource):
    @ns.expect(shop_parser)
    def put(self, id):
        data = shop_parser.parse_args()
        with Session() as session:
            try:
                upsert_shop(session, id, data)
                session.commit()
                return id, 200
            except Exception as e:
                print(e, file=sys.stderr)
                ns.abort(500)

