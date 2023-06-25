from flask_restx import fields


doc = {
    "document": fields.String(),
    "embedding": fields.List(fields.Float, required=False, default=[]),
    "scan_id": fields.String()
}


query_doc = {
    "query_embedding": fields.List(fields.Float, required=True, default=[]),
    "number_of_docs": fields.Integer(required=False, default=4)
}
