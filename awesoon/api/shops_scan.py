
import marshal
from flask_restx import Resource
from awesoon.api.model.scans import scan
from awesoon.api.shops import api
from awesoon.core.database.scans import get_scan_by_id
from awesoon.core.exceptions import ScanNotFoundError
from awesoon.model.schema import Session

scan_model = api.model("scan", scan)


@api.route("<id>/scans/<scan_id>")
class SingleShopScan(Resource):
    def get(self, id, scan_id):
        try:
            with Session() as session:
                scan = get_scan_by_id(session, scan_id, filter={"shop_id": int(id)})
                marshalled_scan = marshal(scan, scan_model)
            return marshalled_scan, 200
        except ScanNotFoundError:
            api.abort(400, "Scan not found")
