from uuid import uuid4
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func, Enum
from awesoon.model.schema import Base
from awesoon.model.schema.utils import MessageType
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    guid = Column(String, default=lambda: str(uuid4()), index=True)
    message_type = Column(Enum(
        *[status.value for status in MessageType],
        name="message_type", create_type=False, validate_strings=True), index=True)
    message = Column(String)
    token_count = Column(Integer)
    timestamp = Column(DateTime, server_default=func.now())
    conversation_id = Column(ForeignKey("conversation_threads.id"))


class Conversation(Base):
    __tablename__ = "conversation_threads"
    id = Column(String, default=lambda: str(uuid4()), index=True, primary_key=True)
    shop_id = Column(ForeignKey("shops.id"))
    timestamp = Column(DateTime, server_default=func.now())
    messages = relationship(
        "Message", foreign_keys=[Message.conversation_id],
        cascade="save-update, merge, delete, delete-orphan",
    )
    shop = relationship(
        "Shop", foreign_keys=[shop_id]
    )

    @hybrid_property
    def ai_message_count(self):
        return sum(1 for message in self.messages if message.message_type == MessageType.AI)

    @hybrid_property
    def user_message_count(self):
        return sum(1 for message in self.messages if message.message_type == MessageType.USER)
