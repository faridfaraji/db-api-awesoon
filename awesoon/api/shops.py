import sys

from flask_restx import Namespace, Resource
from sqlalchemy import select
from flask_restx import Namespace, Resource, marshal, inputs, fields
import sqlalchemy

from awesoon.api.model.shops import shop
from awesoon.api.model.docs import doc, query_doc

from awesoon.core.database.docs import get_closest_shop_doc, get_shop_docs
from awesoon.core.database.shopify import get_all_shopify_app_installations, get_shopify_app_with_name
from awesoon.core.database.shops import (
    delete_negative_keyword,
    get_all_shops,
    get_keywords_for_shop,
    get_shop_with_identifier,
    upsert_shop,
    upsert_shop_negative_keyword,
)
from awesoon.core.exceptions import ShopNotFoundError
from awesoon.model.schema import Session
from awesoon.model.schema.shop import Shop, ShopifyAppInstallation
from awesoon.api.util import add_docs_search_params
from flask_restx import Namespace, Resource, marshal

ns = Namespace("shops", "This namespace is resposible for retrieving and storing the shops info.")

shop_model = ns.model("model", shop)


prompt_parser = ns.parser()
prompt_parser.add_argument("prompt", type=str, default=None, location="json")


shop_parser = ns.parser()
shop_parser.add_argument("shop_name", type=str, default=None, location="json")
shop_parser.add_argument("shop_url", type=str, default=None, location="json")
shop_parser.add_argument("contact_email", type=str, default=None, location="json")


get_shop_parser = ns.parser()
get_shop_parser.add_argument("shop_url", type=str, default=None, location="values")


doc_parser = ns.parser()
doc_parser.add_argument("document", type=str, default=None, location="json")
doc_parser.add_argument("embedding", type=list, default=None, location="json")
doc_parser.add_argument("scan_id", type=str, default=None, location="json")


get_doc_parser = ns.parser()
get_doc_parser = add_docs_search_params(get_doc_parser)


doc_model = ns.model("doc", doc)


query_doc_model = ns.model("closest_doc", query_doc)

query_doc_parser = ns.parser()
query_doc_parser.add_argument("query_embedding", type=list, default=None, location="json")
query_doc_parser.add_argument("number_of_docs", type=int, default=None, location="json")
query_doc_parser = add_docs_search_params(query_doc_parser)

shopify_installation_model = ns.model(
    "shopify_installation",
    {
        "id": fields.String(readonly=True),
        "app_name": fields.String(required=True),
        "access_token": fields.String(required=True),
        "shop_url": fields.String(readonly=True),
    },
)

shopify_installation_parser = ns.parser()
shopify_installation_parser.add_argument("app_name", type=str, default=None, location="json")
shopify_installation_parser.add_argument("access_token", type=str, default=None, location="json")

get_shopify_installation_parser = ns.parser()
get_shopify_installation_parser.add_argument("app_name", type=str, default=None, location="values")


@ns.route("")
class Shops(Resource):
    @ns.expect(get_shop_parser)
    def get(self):
        args = get_shop_parser.parse_args()
        with Session() as session:
            shops = get_all_shops(session, args)
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
                return marshal(docs, doc_model), 200
            except Exception as e:
                print(e, file=sys.stderr)
                ns.abort(500)


@ns.route("/<id>/closest-doc")
class ClosestShopDoc(Resource):
    @ns.expect(query_doc_model)
    def get(self, id):
        with Session() as session:
            try:
                doc_data = query_doc_parser.parse_args()
                embedding = doc_data["query_embedding"]
                number_of_docs = doc_data["number_of_docs"]
                docs = get_closest_shop_doc(session, embedding, id, number_of_docs=number_of_docs)
                return marshal(docs, doc_model)
            except Exception as e:
                print(e, file=sys.stderr)
                ns.abort(500)


@ns.route("/<id>/shopify-installations")
class ShopifyInstallation(Resource):
    @ns.expect(get_shopify_installation_parser)
    def get(self, id):
        with Session() as session:
            try:
                args = get_shopify_installation_parser.parse_args()
                shopify_app_installations = get_all_shopify_app_installations(session, id, args)
                return marshal(shopify_app_installations, shopify_installation_model)
            except Exception as e:
                print(e, file=sys.stderr)
                ns.abort(500)

    @ns.expect(shopify_installation_parser)
    def post(self, id):
        with Session() as session:
            try:
                data = shopify_installation_parser.parse_args()
                shop = get_shop_with_identifier(session, id)
                shopify_app = get_shopify_app_with_name(session, data["app_name"])
                shopify_app_installation = ShopifyAppInstallation(
                    access_token=data["access_token"], shop_id=shop.id, app_id=shopify_app.app_client_id
                )
                session.add(shopify_app_installation)
                session.commit()
                return {"message": "SUCCESS"}, 200
            except sqlalchemy.exc.IntegrityError:
                ns.abort(400, "This installation is not allowed")
            except Exception as e:
                print(e, file=sys.stderr)
                ns.abort(500)
