import sys

from flask import request
from flask_restx import Namespace, Resource
from sqlalchemy import select
from flask_restx import Namespace, Resource, marshal

from awesoon.api.model.shops import shop, shop_prompt
from awesoon.core.database.docs import add_shop_docs, get_shop_docs
from awesoon.core.database.shops import delete_negative_keyword, get_keywords_for_shop, get_shop_with_identifier, upsert_shop, upsert_shop_negative_keyword
from awesoon.core.exceptions import ShopNotFoundError
from awesoon.model.schema import Session
from awesoon.model.schema.shop import Shop
from flask_restx import Namespace, Resource, fields, inputs, marshal
ns = Namespace(
    "shops", "This namespace is resposible for retrieving and storing the shops info.")

shop_model = ns.model(
    "model",
    shop
)

shop_prompt_model = ns.model(
    "model",
    shop_prompt
)

prompt_parser = ns.parser()
prompt_parser.add_argument("prompt", type=str, default=None, location="json")


shop_parser = ns.parser()
shop_parser.add_argument("name", type=str, default=None, location="json")
shop_parser.add_argument("shop_url", type=str, default=None, location="json")
shop_parser.add_argument("access_token", type=str, default=None, location="json")

doc_parser = ns.parser()
doc_parser.add_argument("doc", type=str, default=None, location="json")
doc_parser.add_argument("embedding", type=list, default=None, location="json")
doc_parser.add_argument("version", type=str, default=None, location="json")


doc_model = ns.model(
    "doc",
    {
        "doc": fields.String(),
        "embedding": fields.List(fields.Float, required=False, default=[]),
        "version": fields.String()
    },
)


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
                shop = get_shop_with_identifier(session, int(id))
                marshalled_shop = marshal(shop, shop_model)
            return marshalled_shop, 200
        except ShopNotFoundError:
            ns.abort(404, "Shop Not Found")

    @ns.expect(shop_parser)
    def put(self, id):
        data = shop_parser.parse_args()
        with Session() as session:
            try:
                upsert_shop(session, int(id), data)
                session.commit()
                return id, 200
            except Exception as e:
                print(e, file=sys.stderr)
                ns.abort(500)


@ns.route("/<id>/negative-keywords")
class NegativeKeyWords(Resource):
    def get(self, id):
        with Session() as session:
            keywords = get_keywords_for_shop(session, int(id))
            return keywords, 200


@ns.route("/<id>/negative-keywords/<word>")
class SingleNegativeKeyWord(Resource):
    def put(self, id, word):
        with Session() as session:
            try:
                upsert_shop_negative_keyword(session, word, int(id))
                session.commit()
                return {"message": "SUCCESS"}, 200
            except Exception as e:
                print(e, file=sys.stderr)
                ns.abort(500)

    def delete(self, id, word):
        with Session() as session:
            try:
                delete_negative_keyword(session, word, int(id))
                session.commit()
                return id, 200
            except Exception as e:
                print(e, file=sys.stderr)
                ns.abort(500)


@ns.route("/<id>/docs")
class ShopDoc(Resource):
    def get(self, id):
        with Session() as session:
            try:
                docs = get_shop_docs(session, id)
                session.commit()
                return docs, 200
            except Exception as e:
                print(e, file=sys.stderr)
                ns.abort(500)

    @ns.expect(doc_model)
    def post(self, id):
        with Session() as session:
            try:
                doc_data = doc_parser.parse_args()
                embedding = doc_data["embedding"]
                if len(embedding) != 1536:
                    return 400, "Wrong embedding dimension, should be length 1536"
                add_shop_docs(session, doc_data, id)
                session.commit()
                return {"message": "SUCCESS"}, 200
            except Exception as e:
                print(e, file=sys.stderr)
                ns.abort(500)

