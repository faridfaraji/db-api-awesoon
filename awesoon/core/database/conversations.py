from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session
from awesoon.core.database.shops import get_shop_with_identifier
from awesoon.core.exceptions import ConversationNotFoundError

from awesoon.model.schema.conversations import Conversation, Message
from awesoon.model.schema.shop import Shop

# CONV_COLUMNS = [c.label("id") if c.name == "guid"
#                 else c for c in Conversation.__table__.c if c.name != "id"]


def get_conversations_by_shop(session: Session, shop_id: int):
    query = select(
        Conversation
    ).join(
        Shop, Shop.id == Conversation.shop_id
    ).where(
        Shop.shop_identifier == shop_id
    )
    return session.scalars(query).all()


def get_messages_by_ids(session: Session, message_ids: List[str]) -> List[Message]:
    query = select(
        Message
    ).filter(
        Message.guid.in_(message_ids)
    )
    return session.scalars(query).all()


def get_conversations(session: Session, filter_args: dict):
    query = select(
        Conversation
    )
    if filter_args["shop_id"]:
        query = query.join(Shop, Shop.id == Conversation.shop_id)
        query = query.where(Shop.shop_identifier == filter_args["shop_id"])
    return session.scalars(query).all()


def get_conversation_by_id(session: Session, conversation_id: str):
    query = select(
        Conversation
    ).where(
        Conversation.id == conversation_id
    )
    conversation = session.scalars(query).first()
    if conversation is None:
        raise ConversationNotFoundError
    return conversation


def get_conversation_object_by_id(session: Session, conversation_id: str):
    query = select(
        Conversation
    ).where(
        Conversation.id == conversation_id
    )
    conversation = session.scalars(query).first()
    if conversation is None:
        raise ConversationNotFoundError
    return conversation


def get_conversation_messages(session: Session, conversation_id: str):
    query = select(
        Message
    ).join(
        Conversation, Conversation.id == Message.conversation_id
    ).where(
        Conversation.id == conversation_id
    )
    return session.scalars(query).all()


def add_conversation_message(session: Session, message: dict, conversation_id: str):
    conversation = get_conversation_object_by_id(session, conversation_id)
    message = Message(**message)
    conversation.messages.append(message)
    session.add(conversation)


def add_conversation(session: Session, conversation_data: dict):
    message_ids = conversation_data.pop("messages")
    shop_id = conversation_data.pop("shop_id")
    shop = get_shop_with_identifier(session, shop_id)
    if message_ids:
        pass
    conversation = Conversation(**conversation_data)
    conversation.shop_id = shop.id
    conversation.messages = get_messages_by_ids(session, message_ids)
    session.add(conversation)
    return conversation
