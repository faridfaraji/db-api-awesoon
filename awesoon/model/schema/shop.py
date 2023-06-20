from datetime import datetime
from langchain.vectorstores.pgvector import Base
from sqlalchemy import BigInteger, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from langchain.vectorstores.pgvector import CollectionStore
from uuid import uuid4


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
    name = Column(String)
    shop_identifier = Column(BigInteger, unique=True)
    shop_url = Column(String, unique=True)
    negative_keywords = relationship(
        "ShopNegativeKeyWord",
        foreign_keys=[ShopNegativeKeyWord.shop_id],
    )
    collection_id = Column(ForeignKey(CollectionStore.uuid))
    collection = relationship(
        "CollectionStore", foreign_keys=[collection_id]
    )
    docs_version = Column(String, nullable=True)


class ShopifyApp(Base):
    __tablename__ = "shopify_apps"
    app_client_id = Column(String, primary_key=True)
    app_client_secret = Column(String)
    name = Column(String, unique=True)


class ShopifyAppInstallation(Base):
    __tablename__ = "shopify_app_installations"
    guid = Column(String, default=lambda: str(uuid4()), index=True)
    access_token = Column(String)
    app_id = Column(ForeignKey(ShopifyApp.app_client_id), primary_key=True)
    shop_id = Column(ForeignKey(Shop.id), primary_key=True)
