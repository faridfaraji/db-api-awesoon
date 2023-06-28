import enum

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Enum, Integer, String

from awesoon.model.schema import Base
from awesoon.model.schema.utils import DocType

ADA_TOKEN_COUNT = 1536


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


class DistanceStrategy(str, enum.Enum):
    EUCLIDEAN = Doc.embedding.l2_distance
    COSINE = Doc.embedding.cosine_distance
    MAX_INNER_PRODUCT = Doc.embedding.max_inner_product


DEFAULT_DISTANCE_STRATEGY = DistanceStrategy.COSINE
