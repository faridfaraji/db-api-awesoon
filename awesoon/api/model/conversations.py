import datetime
from flask_restx import fields

from awesoon.model.schema.utils import MessageType


class Message(fields.List):
    __default__ = []

    def format(self, values):
        return [v.guid for v in values]


class Shop(fields.Integer):

    def format(self, value):
        return value.shop_identifier


message = {
    "message_type": fields.String(enum=[enum.value for enum in MessageType], required=True),
    "message": fields.String(),
    "timestamp": fields.DateTime(required=False, readonly=True)
}


conversation = {
    "id": fields.String(readonly=True),
    "shop_id": Shop(attribute="shop"),
    "timestamp": fields.DateTime(required=False, readonly=True),
    "message_type": fields.String(readonly=True),
    "messages": Message(fields.String),
    "ai_message_count": fields.Integer(),
    "user_message_count": fields.Integer()
}


def add_convesation_parser(parser):
    parser.add_argument("shop_id", type=int, default=None, location="json")
    parser.add_argument("messages", type=list, default=None, location="json")
    return parser


def add_message_parser(parser):
    parser.add_argument("message_type", type=str, default=None, location="json")
    parser.add_argument("message", type=str, default=None, location="json")
    return parser


def add_conversation_search_params(parser):
    parser.add_argument("shop_id", type=int, default=None, location="values")
    return parser
