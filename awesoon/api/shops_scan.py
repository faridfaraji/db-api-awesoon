
from flask_restx import Resource, marshal
from awesoon.api.model.scans import scan
from awesoon.api.shops import api
from awesoon.core.database.scans import get_latest_scan, get_scan_by_id, get_scans, get_scans_with_shop_id
from awesoon.core.exceptions import ScanNotFoundError, ShopNotFoundError
from awesoon.model.schema import Session

scan_model = api.model("scan", scan)


@api.route("/<id>/scans/<scan_id>")
class SingleShopScan(Resource):
    def get(self, id, scan_id):
        try:
            with Session() as session:
                scan = get_scan_by_id(session, scan_id, filter={"shop_id": int(id)})
                marshalled_scan = marshal(scan, scan_model)
            return marshalled_scan, 200
        except ScanNotFoundError:
            api.abort(400, "Scan not found")


@api.route("/<id>/scans/latest")
class latestScan(Resource):
    def get(self, id):
        try:
            with Session() as session:
                scan = get_latest_scan(session, int(id))
                marshalled_scan = marshal(scan, scan_model)
            return marshalled_scan, 200
        except ShopNotFoundError:
            api.abort(400, "Scan not found")


@api.route("/<id>/scans")
class ShopScans(Resource):
    def get(self, id):
        try:
            with Session() as session:
                scan = get_scans_with_shop_id(session, int(id))
                marshalled_scan = marshal(scan, scan_model)
            return marshalled_scan, 200
        except ShopNotFoundError:
            api.abort(400, "Scan not found")
