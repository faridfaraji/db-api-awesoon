import logging
import sys

import sqlalchemy
from flask_restx import Namespace, Resource, marshal

from awesoon.api.model.docs import doc, query_doc
from awesoon.api.model.shops import add_shop_parser, shop, shopify_installation
from awesoon.api.model.util import add_paginator
from awesoon.constants import SUCCESS_MESSAGE
from awesoon.core.database.docs import get_closest_shop_doc, get_scan_docs
from awesoon.core.database.scans import get_latest_scan
from awesoon.core.database.shopify import (
    get_all_shopify_app_installations,
    get_shopify_app_with_name,
)
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
from awesoon.model.schema.shop import ShopifyAppInstallation

api = Namespace("shops", "This namespace is responsible for retrieving and storing the shops info.")

#########
shop_model = api.model("model", shop)
doc_model = api.model("doc", doc)
query_doc_model = api.model("closest_doc", query_doc)
shopify_installation_model = api.model("shopify_installation", shopify_installation)
#########

shop_parser = api.parser()
add_shop_parser(shop_parser)


get_shop_parser = api.parser()
get_shop_parser.add_argument("shop_url", type=str, default=None, location="values")


query_doc_parser = api.parser()
query_doc_parser.add_argument("query_embedding", type=list, default=None, location="json")
query_doc_parser.add_argument("number_of_docs", type=int, default=None, location="json")

shopify_installation_parser = api.parser()
shopify_installation_parser.add_argument("app_name", type=str, default=None, location="json")
shopify_installation_parser.add_argument("access_token", type=str, default=None, location="json")

get_shopify_installation_parser = api.parser()
get_shopify_installation_parser.add_argument("app_name", type=str, default=None, location="values")

bot_temperature_parser = api.parser()
bot_temperature_parser.add_argument("bot_temperature", type=float, default=None, location="json")

get_docs_parser = api.parser()
get_docs_parser = add_paginator(get_docs_parser)


@api.route("")
class Shops(Resource):
    @api.expect(get_shop_parser)
    def get(self):
        args = get_shop_parser.parse_args()
        with Session() as session:
            shops = get_all_shops(session, args)
            marshalled_shops = marshal(shops, shop_model)
        return marshalled_shops, 200


@api.route("/<id>")
class SingleShop(Resource):
    def get(self, id):
        try:
            with Session() as session:
                shop = get_shop_with_identifier(session, int(id))
                marshalled_shop = marshal(shop, shop_model)
            return marshalled_shop, 200
        except ShopNotFoundError:
            api.abort(404, "Shop Not Found")

    @api.expect(shop_parser)
    def put(self, id):
        data = shop_parser.parse_args()
        with Session() as session:
            try:
                upsert_shop(session, int(id), data)
                session.commit()
                return id, 200
            except Exception as e:
                print(e, file=sys.stderr)
                api.abort(500)


@api.route("/<id>/negative-keywords")
class NegativeKeyWords(Resource):
    def get(self, id):
        with Session() as session:
            keywords = get_keywords_for_shop(session, int(id))
            return keywords, 200


@api.route("/<id>/negative-keywords/<word>")
class SingleNegativeKeyWord(Resource):
    def put(self, id, word):
        with Session() as session:
            try:
                upsert_shop_negative_keyword(session, word, int(id))
                session.commit()
                return SUCCESS_MESSAGE, 200
            except Exception as e:
                print(e, file=sys.stderr)
                api.abort(500)

    def delete(self, id, word):
        with Session() as session:
            try:
                delete_negative_keyword(session, word, int(id))
                session.commit()
                return id, 200
            except Exception as e:
                print(e, file=sys.stderr)
                api.abort(500)


@api.route("/<id>/docs")
class ShopDoc(Resource):
    @api.marshal_list_with(doc_model)
    def get(self, id):
        with Session() as session:
            try:
                get_docs_params = get_docs_parser.parse_args()
                offset = get_docs_params["offset"]
                limit = get_docs_params["limit"]
                docs = []
                scan = get_latest_scan(session, int(id))
                if scan:
                    docs = get_scan_docs(session, scan[0], offset=offset, limit=limit)
                return marshal(docs, doc_model), 200
            except Exception as e:
                print(e, file=sys.stderr)
                api.abort(500)


@api.route("/<id>/closest-doc")
class ClosestShopDoc(Resource):
    @api.expect(query_doc_model)
    @api.marshal_with(doc_model)
    def post(self, id):
        with Session() as session:
            try:
                doc_data = query_doc_parser.parse_args()
                embedding = doc_data["query_embedding"]
                number_of_docs = doc_data["number_of_docs"]
                docs = get_closest_shop_doc(session, embedding, id, number_of_docs=number_of_docs)
                return marshal(docs, doc_model)
            except Exception as e:
                print(e, file=sys.stderr)
                api.abort(500)


@api.route("/<id>/shopify-installations")
class ShopifyInstallation(Resource):
    @api.expect(get_shopify_installation_parser)
    def get(self, id):
        with Session() as session:
            try:
                args = get_shopify_installation_parser.parse_args()
                shopify_app_installations = get_all_shopify_app_installations(session, id, args)
                return marshal(shopify_app_installations, shopify_installation_model)
            except Exception as e:
                print(e, file=sys.stderr)
                api.abort(500)

    @api.expect(shopify_installation_parser)
    def post(self, id):
        with Session() as session:
            try:
                data = shopify_installation_parser.parse_args()
                shop = get_shop_with_identifier(session, id)
                shopify_app = get_shopify_app_with_name(session, data["app_name"])
                shopify_app_installation = ShopifyAppInstallation(
                    access_token=data["access_token"],
                    shop_id=shop.id,
                    app_id=shopify_app.app_client_id
                )
                session.add(shopify_app_installation)
                session.commit()
                return SUCCESS_MESSAGE, 200
            except sqlalchemy.exc.IntegrityError:
                logging.exception("Integrity Error")
                api.abort(400, "This installation is not allowed")
            except Exception as e:
                print(e, file=sys.stderr)
                api.abort(500)


@api.route("/<id>/bot-temperature")
class BotTemperature(Resource):
    @api.expect(bot_temperature_parser)
    def put(self, id):
        with Session() as session:
            try:
                data = bot_temperature_parser.parse_args()
                shop = get_shop_with_identifier(session, id)
                shop.bot_temperature = data["bot_temperature"]
                session.add(shop)
                session.commit()
                return SUCCESS_MESSAGE, 200
            except sqlalchemy.exc.IntegrityError:
                api.abort(400, "This installation is not allowed")
            except Exception as e:
                print(e, file=sys.stderr)
                api.abort(500)
