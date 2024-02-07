import sys
from copy import copy

from flask_restx import Namespace, Resource, marshal

from awesoon.api.model.docs import add_docs_parser, doc
from awesoon.api.model.scans import scan, scan_status
from awesoon.api.model.util import add_paginator
from awesoon.constants import SUCCESS_MESSAGE
from awesoon.core.database.docs import add_scan_doc, get_scan_docs
from awesoon.core.database.scans import (
    add_scan,
    get_scan_by_id,
    get_scans,
    update_scan,
    update_scan_status,
)
from awesoon.core.exceptions import ScanNotFoundError, ShopNotFoundError
from awesoon.model.schema import Session
from awesoon.model.schema.doc import ADA_TOKEN_COUNT

api = Namespace("scans", "This namespace is responsible for adding and retrieving shop scans")

############
scan_model = api.model("scan", scan)
scan_status_model = api.model("scan_status", scan_status)
doc_model = api.model("doc", doc)
############


scan_status_parser = api.parser()
scan_status_parser.add_argument("status", type=str, default=None, location="json")

scan_parser = copy(scan_status_parser)
scan_parser.add_argument("trigger_type", type=str, default=None, location="json")
scan_parser.add_argument("shop_id", type=int, default=None, location="json")

doc_parser = api.parser()
doc_parser = add_docs_parser(doc_parser)

get_docs_parser = api.parser()
get_docs_parser = add_paginator(get_docs_parser)


@api.route("/<scan_id>")
class SingleScan(Resource):
    def get(self, scan_id):
        try:
            with Session() as session:
                scan = get_scan_by_id(session, scan_id)
                marshalled_scan = marshal(scan, scan_model)
            return marshalled_scan, 200
        except ScanNotFoundError:
            api.abort(404, "Scan Not Found")

    @api.expect(scan_model, validate=True)
    def put(self, scan_id):
        data = scan_parser.parse_args()
        with Session() as session:
            try:
                update_scan(session, scan_id, data)
                session.commit()
                return SUCCESS_MESSAGE, 200
            except Exception as e:
                print(e, file=sys.stderr)
                api.abort(500)


@api.route("")
class Scan(Resource):
    def get(self):
        try:
            with Session() as session:
                scans = get_scans(session)
                marshalled_scans = marshal(scans, scan_model)
            return marshalled_scans, 200
        except ShopNotFoundError:
            api.abort(400, "Shop not found")

    @api.expect(scan_model, validate=True)
    def post(self):
        data = scan_parser.parse_args()
        with Session() as session:
            try:
                scan = add_scan(session, data)
                session.commit()
                return scan.guid, 200
            except ShopNotFoundError:
                api.abort(400, "Shop not found")
            except Exception as e:
                print(e, file=sys.stderr)
                api.abort(500)


@api.route("/<scan_id>/status")
class ScanStatus(Resource):
    def get(self, scan_id):
        try:
            with Session() as session:
                scan = get_scan_by_id(session, scan_id)
                marshalled_scans = marshal(scan, scan_status_model)
            return marshalled_scans, 200
        except ScanNotFoundError:
            api.abort(400, "Scan Not Found")

    @api.expect(scan_status_model, validate=True)
    def put(self, scan_id):
        data = scan_status_parser.parse_args()
        with Session() as session:
            try:
                update_scan_status(session, scan_id, data["status"])
                session.commit()
                return SUCCESS_MESSAGE, 200
            except Exception as e:
                print(e, file=sys.stderr)
                api.abort(500)


@api.route("/<scan_id>/docs")
class ScanDoc(Resource):
    @api.marshal_list_with(doc_model)
    @api.expect(get_docs_parser)
    def get(self, scan_id):
        with Session(autoflush=False, expire_on_commit=False) as session:
            try:
                get_docs_params = get_docs_parser.parse_args()
                offset = get_docs_params["offset"]
                limit = get_docs_params["limit"]
                docs = get_scan_docs(session, scan_id, offset=offset, limit=limit)
                session.close()
                return marshal(docs, doc_model), 200
            except Exception as e:
                print(e, file=sys.stderr)
                api.abort(500)

    @api.expect([doc_model], validate=True)
    def post(self, scan_id):
        try:
            with Session() as session:
                docs_data = api.payload
                for doc_data in docs_data:
                    embedding = doc_data["embedding"]
                    if len(embedding) != ADA_TOKEN_COUNT:
                        api.abort(400, f"Wrong embedding dimension, should be length {ADA_TOKEN_COUNT}")
                for doc_data in docs_data:
                    add_scan_doc(session, doc_data, scan_id)
                session.commit()
        except Exception as e:
            print(e, file=sys.stderr)
            api.abort(500)
        return SUCCESS_MESSAGE, 200

