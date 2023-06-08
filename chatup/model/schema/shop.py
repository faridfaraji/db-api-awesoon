from chatup.model import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


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
    shop_identifier = Column(Integer, unique=True)
    shop_url = Column(String)
    access_token = Column(String)
    description = Column(String)
    negative_keywords = relationship(
        "ShopNegativeKeyWord",
        foreign_keys=[ShopNegativeKeyWord.shop_id],
    )
