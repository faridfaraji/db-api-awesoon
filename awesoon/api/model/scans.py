from flask_restx import fields
from datetime import datetime

from awesoon.model.schema.utils import ScanStatus, TriggerType

scan = {
    "id": fields.String(readonly=True),
    "trigger_type": fields.String(enum=[enum.value for enum in TriggerType], required=True),
    "status": fields.String(enum=[enum.value for enum in ScanStatus], required=True),
    "shop_id": fields.Integer(),
    "timestamp": fields.DateTime(readonly=True),
}

scan_status = {
    "status": fields.String(enum=[enum.value for enum in ScanStatus], required=True),
}
