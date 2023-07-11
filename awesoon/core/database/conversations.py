from typing import List
from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from awesoon.core.database.shops import get_shop_with_identifier
from awesoon.core.exceptions import ConversationNotFoundError
from awesoon.model.schema.conversations import Conversation, Message
from awesoon.model.schema.shop import Shop


def get_conversations_by_shop(session: Session, shop_id: int):
    query = (
        select(Conversation)
        .join(Shop, Shop.id == Conversation.shop_id)
        .where(Shop.shop_identifier == shop_id)
        .order_by(desc(Conversation.timestamp))
    )
    return session.scalars(query).all()


def get_messages_by_ids(session: Session, message_ids: List[str]) -> List[Message]:
    query = select(Message).filter(Message.guid.in_(message_ids))
    return session.scalars(query).all()


def get_conversations(session: Session, filter_args: dict):
    query = (
        select(Conversation)
        .order_by(desc(Conversation.timestamp))
    )
    if filter_args["shop_id"]:
        query = query.join(Shop, Shop.id == Conversation.shop_id)
        query = query.where(Shop.shop_identifier == filter_args["shop_id"])

    if filter_args.get("start_datetime") and filter_args.get("end_datetime"):
        start_datetime = filter_args["start_datetime"]
        end_datetime = filter_args["end_datetime"]
        query = query.where(Conversation.timestamp >= start_datetime)
        query = query.where(Conversation.timestamp <= end_datetime)
    return session.scalars(query).all()


def get_conversation_by_id(session: Session, conversation_id: str, filter_args: dict = None):
    query = select(Conversation).where(Conversation.id == conversation_id)
    if filter_args and filter_args["shop_id"]:
        query = query.join(Shop, Shop.id == Conversation.shop_id)
        query = query.where(Shop.shop_identifier == filter_args["shop_id"])
    conversation = session.scalars(query).first()
    if conversation is None:
        raise ConversationNotFoundError
    return conversation


def get_conversation_messages(session: Session, conversation_id: str, filter_args: dict = None):
    query = (
        select(Message)
        .join(Conversation, Conversation.id == Message.conversation_id)
        .where(Conversation.id == conversation_id)
        .order_by(desc(Message.timestamp))
    )
    if filter_args and filter_args["shop_id"]:
        query = query.join(Shop, Shop.id == Conversation.shop_id)
        query = query.where(Shop.shop_identifier == filter_args["shop_id"])
    return session.scalars(query).all()


def add_conversation_message(session: Session, message: dict, conversation_id: str):
    conversation = get_conversation_by_id(session, conversation_id)
    message = Message(**message)
    conversation.messages.append(message)
    session.add(conversation)


def add_conversation(session: Session, conversation_data: dict):
    message_ids = conversation_data.pop("messages")
    shop_id = conversation_data.pop("shop_id")
    shop = get_shop_with_identifier(session, shop_id)
    conversation = Conversation(**conversation_data)
    conversation.shop_id = shop.id
    conversation.messages = get_messages_by_ids(session, message_ids)
    session.add(conversation)
    return conversation


def get_shop_messages(session: Session, shop_id: str, filter_args: dict = None):
    query = (
        select(Message)
        .join(Conversation, Conversation.id == Message.conversation_id)
        .join(Shop, Shop.id == Conversation.shop_id)
        .where(Shop.shop_identifier == shop_id)
        .order_by(desc(Message.timestamp))
    )
    if filter_args.get("start_datetime") and filter_args.get("end_datetime"):
        start_datetime = filter_args["start_datetime"]
        end_datetime = filter_args["end_datetime"]
        query = query.where(Message.timestamp >= start_datetime)
        query = query.where(Message.timestamp <= end_datetime)
    return session.scalars(query).all()
