from uuid import uuid4
from langchain.vectorstores.pgvector import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Enum
from awesoon.model.schema.doc_enums import DocType
from langchain.vectorstores.pgvector import CollectionStore

from pgvector.sqlalchemy import Vector

ADA_TOKEN_COUNT = 2


class Doc(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    doc_type = Column(Enum(
        *[status.value for status in DocType],
        name="doc_type", create_type=False, validate_strings=True), index=True)
    doc_identifier = Column(String)
    hash = Column(String)
    embedding: Vector = Column(Vector(ADA_TOKEN_COUNT))
    document = Column(String, nullable=True)
