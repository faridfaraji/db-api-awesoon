from uuid import uuid4

from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from awesoon.model.schema import Base
from awesoon.model.schema.conversations import Conversation
from awesoon.model.schema.scan import Scan
from sqlalchemy.ext.hybrid import hybrid_property


class ShopNegativeKeyWord(Base):
    __tablename__ = "shop_nk_associations"
    shop_id = Column(ForeignKey("shops.id"), primary_key=True)
    negative_keyword = Column(ForeignKey("negative_keywords.word"), primary_key=True)


class NegativeKeyWord(Base):
    __tablename__ = "negative_keywords"
    word = Column(String, primary_key=True)


class Shop(Base):
    __tablename__ = "shops"
    id = Column(Integer, primary_key=True)
    shop_name = Column(String)
    contact_email = Column(String)
    shop_identifier = Column(BigInteger, unique=True)
    shop_url = Column(String, unique=True)
    negative_keywords = relationship(
        "ShopNegativeKeyWord",
        foreign_keys=[ShopNegativeKeyWord.shop_id],
    )
    latest_scan_id = Column(ForeignKey(Scan.guid))
    conversations = relationship(
        "Conversation", foreign_keys=[Conversation.shop_id],
        cascade="save-update, merge, delete, delete-orphan",
    )

    @hybrid_property
    def conversations_count(self):
        return len(self.conversations)


class ShopifyApp(Base):
    __tablename__ = "shopify_apps"
    app_client_id = Column(String, primary_key=True)
    app_client_secret = Column(String)
    app_name = Column(String, unique=True)


class ShopifyAppInstallation(Base):
    __tablename__ = "shopify_app_installations"
    guid = Column(String, default=lambda: str(uuid4()), index=True)
    access_token = Column(String)
    app_id = Column(ForeignKey(ShopifyApp.app_client_id), primary_key=True)
    shop_id = Column(ForeignKey(Shop.id), primary_key=True)
