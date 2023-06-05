from chatup.model import Base
from sqlalchemy import Column, Integer, String


class Shop(Base):
    __tablename__ = "shops"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    shop_id = Column(Integer, unique=True)
    shop_url = Column(String)
    access_token = Column(String)
    description = Column(String)
