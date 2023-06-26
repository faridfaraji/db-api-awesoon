from flask_restx import fields

from awesoon.model.schema.scan_enums import ScanStatus, TriggerType

scan = {
    "id": fields.String(readonly=True),
    "trigger_type": fields.String(enum=[enum.value for enum in TriggerType], required=True),
    "status": fields.String(enum=[enum.value for enum in ScanStatus], required=True),
    "shop_id": fields.Integer()
}

scan_status = {
    "status": fields.String(enum=[enum.value for enum in ScanStatus], required=True),
}
