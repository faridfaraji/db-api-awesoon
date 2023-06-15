import sys

from flask_restx import Namespace, Resource
from sqlalchemy import select
from flask_restx import Namespace, Resource, marshal, inputs

from awesoon.api.model.shops import shop
from awesoon.api.model.docs import doc, query_doc

from awesoon.core.database.docs import add_shop_docs, get_closest_shop_doc, get_shop_docs
from awesoon.core.database.shops import delete_negative_keyword, get_keywords_for_shop, get_shop_with_identifier, upsert_shop, upsert_shop_negative_keyword
from awesoon.core.exceptions import ShopNotFoundError
from awesoon.model.schema import Session
from awesoon.model.schema.shop import Shop
from awesoon.api.util import add_docs_search_params
from flask_restx import Namespace, Resource, marshal

ns = Namespace(
    "shops", "This namespace is resposible for retrieving and storing the shops info.")

shop_model = ns.model(
    "model",
    shop
)


prompt_parser = ns.parser()
prompt_parser.add_argument("prompt", type=str, default=None, location="json")


shop_parser = ns.parser()
shop_parser.add_argument("name", type=str, default=None, location="json")
shop_parser.add_argument("shop_url", type=str, default=None, location="json")
shop_parser.add_argument("access_token", type=str, default=None, location="json")

doc_parser = ns.parser()
doc_parser.add_argument("document", type=str, default=None, location="json")
doc_parser.add_argument("embedding", type=list, default=None, location="json")
doc_parser.add_argument("docs_version", type=str, default=None, location="json")


get_doc_parser = ns.parser()
get_doc_parser = add_docs_search_params(get_doc_parser)


doc_model = ns.model(
    "doc",
    doc
)


query_doc_model = ns.model(
    "closest_doc",
    query_doc
)

query_doc_parser = ns.parser()
query_doc_parser.add_argument("query_embedding", type=list, default=None, location="json")
query_doc_parser.add_argument("number_of_docs", type=int, default=None, location="json")
query_doc_parser = add_docs_search_params(query_doc_parser)


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
    @ns.expect(get_doc_parser)
    def get(self, id):
        with Session() as session:
            try:
                args = get_doc_parser.parse_args()
                docs = get_shop_docs(session, id, args)
                session.commit()
                return marshal(docs, doc_model), 200
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


@ns.route("/<id>/closest-doc")
class ClosestShopDoc(Resource):
    @ns.expect(query_doc_model)
    def post(self, id):
        with Session() as session:
            try:
                doc_data = query_doc_parser.parse_args()
                embedding = doc_data["query_embedding"]
                number_of_docs = doc_data["number_of_docs"]
                docs = get_closest_shop_doc(session, embedding, id, number_of_docs=number_of_docs)
                texts = [doc.page_content for doc in docs]
                return {"documents": texts}, 200
            except Exception as e:
                print(e, file=sys.stderr)
                ns.abort(500)
