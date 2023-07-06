from flask_restx import Resource, marshal
from flask import request
from awesoon.api.model.conversations import message, conversation
from awesoon.api.util import add_date_search_params
from awesoon.api.shops_scan import api
from awesoon.core.database.conversations import get_conversation_by_id, get_conversation_messages, get_conversations
from awesoon.core.exceptions import ConversationNotFoundError
from awesoon.model.schema import Session
from datetime import datetime, timedelta

conversation_model = api.model("scan", conversation)
message_model = api.model("message_model", message)

date_parser = api.parser()
get_conversation_parser = add_date_search_params(get_conversation_parser)


@api.route("/<id>/conversations/<conversation_id>")
class SingleShopConversation(Resource):
    def get(self, id, conversation_id):
        try:
            with Session() as session:
                conversation = get_conversation_by_id(session, conversation_id, filter_args={"shop_id": int(id)})
                marshalled_conversation = marshal(conversation, conversation_model)
            return marshalled_conversation, 200
        except ConversationNotFoundError:
            api.abort(400, "conversation not found")


@api.route("/<id>/conversations")
class ShopConversations(Resource):
    def get(self, id):
        try:
            args = get_conversation_parser.parse_args()
            args["shop_id"] = int(id)

            with Session() as session:
                conversations = get_conversations(session, filter_args=filter_args)
                marshalled_conversation = marshal(conversations, conversation_model)
            return marshalled_conversation, 200
        except ConversationNotFoundError:
            api.abort(400, "conversation not found")


@api.route("/<id>/conversations/<conversation_id>/messages")
class ConversationMessages(Resource):
    @api.marshal_list_with(message_model)
    def get(self, id, conversation_id):
        try:
            with Session() as session:
                messages = get_conversation_messages(session, conversation_id, filter_args={"shop_id": int(id)})
                return messages, 200
        except ConversationNotFoundError:
            api.abort(400, "Shop not found")
