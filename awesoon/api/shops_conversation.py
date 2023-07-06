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
date_paser = add_date_search_params(date_parser)


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
            args = date_parser.parse_args()
            # Extract the filter dates from the request query parameters
            start_datetime_str = args.get("start_datetime")
            end_datetime_str = args.get("end_datetime")

            if start_datetime_str:
                start_datetime = datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M:%S")
            else:
                # Set default start datetime as 24 hours ago
                start_datetime = datetime.now() - timedelta(days=1)

            if end_datetime_str:
                end_datetime = datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M:%S")
            else:
                # Set default end datetime as current datetime
                end_datetime = datetime.now()

            filter_args = {"shop_id": int(id), "start_datetime": start_datetime, "end_datetime": end_datetime}

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
