import sys
from copy import copy

from flask_restx import Namespace, Resource, marshal

from awesoon.api.model.docs import add_docs_parser, doc
from awesoon.api.model.scans import scan, scan_status
from awesoon.api.util import add_docs_search_params
from awesoon.constants import SUCCESS_MESSAGE
from awesoon.core.database.docs import add_scan_doc, get_scan_docs
from awesoon.core.database.scans import (
    add_scan,
    get_scan_by_id,
    get_scans,
    get_scans_with_shop_id,
    update_scan,
    update_scan_status,
)
from awesoon.core.exceptions import ScanNotFoundError, ShopNotFoundError
from awesoon.model.schema import Session
from awesoon.model.schema.doc import ADA_TOKEN_COUNT

ns = Namespace("scans", "This namespace is resposible for adding and retrieving shop scans")

############
scan_model = ns.model("scan", scan)
scan_status_model = ns.model("scan_status", scan_status)
doc_model = ns.model("doc", doc)
############


scan_status_parser = ns.parser()
scan_status_parser.add_argument("status", type=str, default=None, location="json")

scan_parser = copy(scan_status_parser)
scan_parser.add_argument("trigger_type", type=str, default=None, location="json")
scan_parser.add_argument("shop_id", type=int, default=None, location="json")

get_doc_parser = ns.parser()
get_doc_parser = add_docs_search_params(get_doc_parser)

doc_parser = ns.parser()
add_docs_parser(doc_parser)



@ns.route("/<scan_id>")
class SingleScan(Resource):
    def get(self, scan_id):
        try:
            with Session() as session:
                scan = get_scan_by_id(session, scan_id)
                marshalled_scan = marshal(scan, scan_model)
            return marshalled_scan, 200
        except ScanNotFoundError:
            ns.abort(404, "Scan Not Found")

    @ns.expect(scan_model, validate=True)
    def put(self, scan_id):
        data = scan_parser.parse_args()
        with Session() as session:
            try:
                update_scan(session, scan_id, data)
                session.commit()
                return SUCCESS_MESSAGE, 200
            except Exception as e:
                print(e, file=sys.stderr)
                ns.abort(500)


@ns.route("")
class Scan(Resource):
    def get(self):
        try:
            with Session() as session:
                scans = get_scans(session)
                marshalled_scans = marshal(scans, scan_model)
            return marshalled_scans, 200
        except ShopNotFoundError:
            ns.abort(400, "Shop not found")

    @ns.expect(scan_model, validate=True)
    def post(self):
        data = scan_parser.parse_args()
        with Session() as session:
            try:
                scan = add_scan(session, data)
                session.commit()
                return scan.guid, 200
            except ShopNotFoundError:
                ns.abort(400, "Shop not found")
            except Exception as e:
                print(e, file=sys.stderr)
                ns.abort(500)


@ns.route("/<scan_id>/status")
class ScanStatus(Resource):
    def get(self, scan_id):
        try:
            with Session() as session:
                scan = get_scan_by_id(session, scan_id)
                marshalled_scans = marshal(scan, scan_status_model)
            return marshalled_scans, 200
        except ScanNotFoundError:
            ns.abort(400, "Scan Not Found")

    @ns.expect(scan_status_model, validate=True)
    def put(self, scan_id):
        data = scan_status_parser.parse_args()
        with Session() as session:
            try:
                update_scan_status(session, scan_id, data["status"])
                session.commit()
                return SUCCESS_MESSAGE, 200
            except Exception as e:
                print(e, file=sys.stderr)
                ns.abort(500)


@ns.route("/<scan_id>/docs")
class ScanDoc(Resource):
    @ns.expect(get_doc_parser)
    def get(self, scan_id):
        with Session() as session:
            try:
                args = get_doc_parser.parse_args()
                docs = get_scan_docs(session, scan_id)
                session.commit()
                return marshal(docs, doc_model), 200
            except Exception as e:
                print(e, file=sys.stderr)
                ns.abort(500)

    @ns.expect(doc_model)
    def post(self, scan_id):
        with Session() as session:
            try:
                doc_data = doc_parser.parse_args()
                embedding = doc_data["embedding"]
                if len(embedding) != ADA_TOKEN_COUNT:
                    ns.abort(400, f"Wrong embedding dimension, should be length {ADA_TOKEN_COUNT}")
                add_scan_doc(session, doc_data, scan_id)
                session.commit()
                return SUCCESS_MESSAGE, 200
            except Exception as e:
                print(e, file=sys.stderr)
                ns.abort(500)

