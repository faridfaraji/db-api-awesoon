from flask_restx import fields
from awesoon.model.schema.utils import DocType


doc = {
    "id": fields.String(readonly=True),
    "document": fields.String(),
    "embedding": fields.List(fields.Float, required=False, default=[]),
    "hash": fields.String(),
    "doc_type": fields.String(enum=[enum.value for enum in DocType], required=True),
    "doc_identifier": fields.String(),
}


query_doc = {
    "query_embedding": fields.List(fields.Float, required=True, default=[]),
    "number_of_docs": fields.Integer(required=False, default=4)
}


def add_docs_parser(parser):
    parser.add_argument("document", type=str, default=None, location="json")
    parser.add_argument("embedding", type=list, default=None, location="json")
    parser.add_argument("hash", type=str, default=None, location="json")
    parser.add_argument("doc_type", type=str, default=None, location="json")
    parser.add_argument("doc_identifier", type=str, default=None, location="json")
    return parser


