
import sys

from flask_restx import Namespace, Resource, marshal
from awesoon.api.model.conversations import add_conversation_search_params, add_conversation_parser, add_conversation_summary_parser, add_message_parser, message, summary, get_conversation_model

from awesoon.constants import SUCCESS_MESSAGE
from awesoon.core.database.conversations import add_conversation, add_conversation_message, get_conversation_by_id, get_conversation_messages, get_conversation_summary, get_conversations, upsert_conversation_summary
from awesoon.core.exceptions import ConversationNotFoundError, ShopNotFoundError
from awesoon.model.schema import Session
import logging


api = Namespace("conversations", "This namespace is responsible for adding and retrieving "
                "conversations and messages of User and AI")
############
message_model = api.model("message_model", message)
conversation_summary_model = api.model("conversation_summary_model", summary)
conversation_model = api.model("conversation_model", get_conversation_model(conversation_summary_model))
summary_model = api.model("summary_model", summary)
############

conversation_parser = api.parser()
message_parser = api.parser()
get_conversation_parser = api.parser()
conversation_parser = add_conversation_parser(conversation_parser)
message_parser = add_message_parser(message_parser)
get_conversation_parser = add_conversation_search_params(get_conversation_parser)

conv_summary_parser = api.parser()
conv_summary_parser = add_conversation_summary_parser(conv_summary_parser)


@api.route("")
class Conversation(Resource):
    @api.expect(get_conversation_parser)
    def get(self):
        args = get_conversation_parser.parse_args()
        with Session() as session:
            conversations = get_conversations(session, args)
            return marshal(conversations, conversation_model), 200

    @api.expect(conversation_model)
    def post(self):
        data = conversation_parser.parse_args()
        with Session() as session:
            try:
                conversation = add_conversation(session, data)
                session.commit()
                return conversation.id, 200
            except ShopNotFoundError:
                logging.exception("Shop Not Found")
                api.abort(404, "Shop Not Found")
            except Exception as e:
                print(e, file=sys.stderr)
                api.abort(500)


@api.route("/<conversation_id>")
class SingleConversation(Resource):
    def get(self, conversation_id):
        with Session() as session:
            conversation = get_conversation_by_id(session, conversation_id)
            return marshal(conversation, conversation_model), 200


@api.route("/<conversation_id>/messages")
class ConversationMessages(Resource):
    @api.marshal_list_with(message_model)
    def get(self, conversation_id):
        try:
            with Session() as session:
                messages = get_conversation_messages(session, conversation_id)
                return messages, 200
        except ConversationNotFoundError:
            api.abort(400, "Shop not found")

    @api.expect(message_model, validate=True)
    def post(self, conversation_id):
        data = message_parser.parse_args()
        with Session() as session:
            try:
                add_conversation_message(session, data, conversation_id)
                session.commit()
                return SUCCESS_MESSAGE, 200
            except ConversationNotFoundError:
                api.abort(400, "Shop not found")
            except Exception as e:
                print(e, file=sys.stderr)
                api.abort(500)


@api.route("/<conversation_id>/summary")
class ConversationSummary(Resource):
    @api.marshal_list_with(summary_model)
    def get(self, conversation_id):
        try:
            with Session() as session:
                conversation_summary = get_conversation_summary(session, conversation_id)
                return marshal(conversation_summary, summary_model), 200
        except ConversationNotFoundError:
            api.abort(400, "Shop not found")

    @api.expect(summary_model, validate=True)
    def put(self, conversation_id):
        data = conv_summary_parser.parse_args()
        with Session() as session:
            try:
                upsert_conversation_summary(session, conversation_id, data)
                session.commit()
                return SUCCESS_MESSAGE, 200
            except ConversationNotFoundError:
                api.abort(400, "Shop not found")
            except Exception as e:
                print(e, file=sys.stderr)
                api.abort(500)
