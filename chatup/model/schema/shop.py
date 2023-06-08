from chatup.model import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


class ShopNegativeKeyWord(Base):
    __tablename__ = "shop_nk_association"
    nk_id = Column(ForeignKey('negative_keywords.id'), primary_key=True)
    shop_id = Column(ForeignKey('shops.id'), primary_key=True)
    shop = relationship("Shop", back_populates="negative_keywords")
    negative_keyword = relationship("NegativeKeyWord", back_populates="shops")


class NegativeKeyWord(Base):
    __tablename__ = "negative_keywords"
    id = Column(Integer, primary_key=True)
    word = Column(String, unique=True)
    shops = relationship(
        "ShopNegativeKeyWord",
        back_populates="negative_keyword",
    )


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
        back_populates="shop",
    )
