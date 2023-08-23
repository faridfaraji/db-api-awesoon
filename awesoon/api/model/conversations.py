from datetime import datetime
from flask_restx import fields, inputs

from awesoon.model.schema.utils import MessageType


class Shop(fields.Integer):
    def format(self, value):
        return value.shop_identifier


message = {
    "message_type": fields.String(enum=[enum.value for enum in MessageType], required=True),
    "message": fields.String(),
    "timestamp": fields.DateTime(default=datetime.utcnow()),
    "metadata": fields.List(fields.String, required=False, default=[], attribute="message_metadata")
}


summary = {
    "title": fields.String(required=True),
    "classifications": fields.String(required=True),
    "summary": fields.String(required=True),
    "satisfaction": fields.String(required=True)
}


def get_conversation_model(summary_model):
    conversation = {
        "id": fields.String(readonly=True),
        "shop_id": Shop(attribute="shop"),
        "timestamp": fields.DateTime(required=False, readonly=True),
        "ai_message_count": fields.Integer(readonly=True),
        "user_message_count": fields.Integer(readonly=True),
        "conversation_summary": fields.Nested(summary_model, readonly=True)
    }
    return conversation


def add_conversation_parser(parser):
    parser.add_argument("shop_id", type=int, default=None, location="json")
    return parser


def add_message_parser(parser):
    parser.add_argument("message_type", type=str, default=None, location="json")
    parser.add_argument("message", type=str, default=None, location="json")
    parser.add_argument("timestamp", type=str, default=None, location="json")
    parser.add_argument("metadata", type=list, default=[], location="json", dest="message_metadata")
    return parser


def add_conversation_search_params(parser):
    parser.add_argument("shop_id", type=int, default=None, location="values")
    return parser


def add_conversation_summary_parser(parser):
    parser.add_argument("title", type=str, default=None, location="json")
    parser.add_argument("classifications", type=str, default=None, location="json")
    parser.add_argument("summary", type=str, default=None, location="json")
    parser.add_argument("satisfaction", type=str, default=None, location="json")
    return parser
