from uuid import uuid4
from langchain.vectorstores.pgvector import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Enum
from awesoon.model.schema.scan_enums import ScanStatus, TriggerType
from langchain.vectorstores.pgvector import CollectionStore


class Scan(Base):
    __tablename__ = "scans"
    guid = Column(String, default=lambda: str(uuid4()), index=True, primary_key=True)
    status = Column(Enum(
        *[status.value for status in ScanStatus],
        name="scan_status", create_type=False, validate_strings=True), index=True)
    trigger_type = Column(Enum(
        *[trigger.value for trigger in TriggerType],
        name="trigger_type", create_type=False, validate_strings=True), index=True)
    shop_id = Column(ForeignKey("shops.id"))


class ScanDoc(Base):
    __tablename__ = "scan_documents"
    guid = Column(String, default=lambda: str(uuid4()), index=True)
    scan_id = Column(String, ForeignKey('scans.guid'), primary_key=True)
    doc_id = Column(Integer, ForeignKey('documents.id'), primary_key=True)
