from flask_restx import Resource, marshal
from flask import request
from awesoon.api.model.conversations import message, conversation
from awesoon.api.model.util import add_date_search_params
from awesoon.api.shops_scan import api
from awesoon.api.util import cached
from awesoon.core.database.conversations import get_conversation_by_id, get_conversation_messages, get_conversations, get_shop_messages
from awesoon.core.database.shops import get_shop_with_identifier
from awesoon.core.exceptions import ConversationNotFoundError, ShopNotFoundError
from awesoon.model.schema import Session


conversation_model = api.model("conversation", conversation)
message_model = api.model("message_model", message)

get_conversation_parser = api.parser()
add_date_search_params(get_conversation_parser)

get_messages_parser = api.parser()
add_date_search_params(get_messages_parser)


@api.route("/<id>/conversations/<conversation_id>")
class SingleShopConversation(Resource):
    @cached
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
    @api.expect(get_conversation_parser)
    @cached
    def get(self, id):
        try:
            add_date_search_params(get_conversation_parser)
            args = get_conversation_parser.parse_args()
            args["shop_id"] = int(id)
            with Session() as session:
                get_shop_with_identifier(session, int(id))
                conversations = get_conversations(session, filter_args=args)
                marshalled_conversation = marshal(conversations, conversation_model)
            return marshalled_conversation, 200
        except ConversationNotFoundError:
            api.abort(400, "conversation not found")
        except ShopNotFoundError:
            api.abort(400, "Shop not found")


@api.route("/<id>/conversations/<conversation_id>/messages")
class ConversationMessages(Resource):
    @api.marshal_list_with(message_model)
    def get(self, id, conversation_id):
        try:
            with Session() as session:
                get_shop_with_identifier(session, int(id))
                messages = get_conversation_messages(session, conversation_id, filter_args={"shop_id": int(id)})
                return messages, 200
        except ConversationNotFoundError:
            api.abort(400, "Shop not found")
        except ShopNotFoundError:
            api.abort(400, "Shop not found")


@api.route("/<id>/messages")
class ShopMessages(Resource):
    @api.marshal_list_with(message_model)
    @api.expect(get_messages_parser)
    @cached
    def get(self, id):
        try:
            add_date_search_params(get_messages_parser)
            args = get_messages_parser.parse_args()
            with Session() as session:
                get_shop_with_identifier(session, int(id))
                messages = get_shop_messages(session, int(id), filter_args=args)
                marshalled_messages = marshal(messages, message_model)
                return marshalled_messages, 200
        except ShopNotFoundError:
            api.abort(400, "Shop not found")
