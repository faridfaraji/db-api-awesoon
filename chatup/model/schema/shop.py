from chatup.model import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


class NegativeKeyWord(Base):
    __tablename__ = "negative_keywords"
    id = Column(Integer, primary_key=True)
    word = Column(String, unique=True)


class ShopNegativeKeyWord(Base):
    __tablename__ = "shop_nk_association"
    nk_id = Column(ForeignKey('negative_keywords.id'), primary_key=True)
    shop_id = Column(ForeignKey('shops.id'), primary_key=True)
    shops = relationship(
        "Shop",
        foreign_keys=[shop_id],
        back_populates="negative_keywords",
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
        "NegativKeyWords",
        foreign_keys=[ShopNegativKeyWord.shop_id],
        back_populates="shops",
    )
