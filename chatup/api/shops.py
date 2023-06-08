import sys

from flask import request
from flask_restx import Namespace, Resource
from sqlalchemy import select
from flask_restx import Namespace, Resource, marshal

from chatup.api.model.shops import shop
from chatup.core.database.shops import get_shop_with_shopify_id, upsert_shop, upsert_shop_negative_keyword
from chatup.core.exceptions import ShopNotFoundError
from chatup.model.schema import Session
from chatup.model.schema.shop import NegativKeyWord, NegativeKeyWord, Shop
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
    def get(self, id):
        try:
            with Session() as session:
                shop = get_shop_with_shopify_id(session, id)
                marshalled_shop = marshal(shop, shop_model)
            return marshalled_shop, 200
        except ShopNotFoundError:
            ns.abort(404, "Shop Not Found")

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


@ns.route("/<id>/negative-keywords")
class NegativeKeyWords(Resource):
    def get(self):
        with Session() as session:
            query = select(NegativeKeyWord)
            words = session.scalars(query).all()
            marshalled_shops = marshal(words, shop_model)
        return marshalled_shops, 200


@ns.route("/<id>/negative-keywords/<word>")
class SingleNegativeKeyWord(Resource):

    @ns.expect(shop_parser)
    def put(self, id, word):
        with Session() as session:
            try:
                upsert_shop_negative_keyword(session, word, id)
                session.commit()
                return id, 200
            except Exception as e:
                print(e, file=sys.stderr)
                ns.abort(500)

    def delete(self, id, word):
        with Session() as session:
            try:
                delete_negative_keyword(session, id, word)
                session.commit()
                return id, 200
            except Exception as e:
                print(e, file=sys.stderr)
                ns.abort(500)

