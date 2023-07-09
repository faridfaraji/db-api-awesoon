from typing import List

import sqlalchemy
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from awesoon.core.database.scans import get_scan_object_by_scan_id
from awesoon.core.exceptions import DocNotFoundError
from awesoon.model.schema.doc import DEFAULT_DISTANCE_STRATEGY, Doc
from awesoon.model.schema.scan import Scan, ScanDoc
from awesoon.model.schema.shop import Shop

DOC_COLUMNS = [c.label("id") if c.name == "guid"
               else c for c in Doc.__table__.c if c.name != "id"]


def get_closest_shop_doc(
    session: Session, embedding: List[float], shop_id: int, number_of_docs: int = 4
):

    query = select(
        *DOC_COLUMNS, ScanDoc.guid.label("id"),
        DEFAULT_DISTANCE_STRATEGY(embedding).label("distance")
    ).order_by(
        sqlalchemy.asc("distance")
    ).join(
        ScanDoc, ScanDoc.doc_id == Doc.id
    ).join(
        Scan, Scan.guid == ScanDoc.scan_id
    ).join(
        Shop, Shop.latest_scan_id == Scan.guid
    ).where(
        Shop.shop_identifier == shop_id
    ).limit(number_of_docs)

    return session.execute(query).all()


def add_scan_doc(session: Session, doc: dict, scan_id: str):
    scan = get_scan_object_by_scan_id(session, scan_id)
    doc = Doc(**doc)
    session.add(doc)
    session.flush()
    scan_doc = ScanDoc(scan_id=scan.guid, doc_id=doc.id)
    session.add(scan_doc)


def get_scan_docs(session: Session, scan_id: str):
    query = (
        select(*DOC_COLUMNS, ScanDoc.guid.label("id"))
        .join(ScanDoc, ScanDoc.doc_id == Doc.id)
        .join(Scan, Scan.guid == ScanDoc.scan_id)
        .where(Scan.guid == scan_id)
    )
    result = session.execute(query).all()
    return result


def update_doc(session: Session, doc: dict, doc_id: str):
    query = select(ScanDoc).where(ScanDoc.guid == doc_id)
    scan_doc = session.scalars(query).first()
    if scan_doc is None:
        raise DocNotFoundError()
    doc = Doc(**doc)
    session.add(doc)
    session.flush()
    scan_doc.doc_id = doc.id
    session.add(scan_doc)
    return scan_doc


def get_shop_docs(session: Session, shop_id: int):
    query = (
        select(*DOC_COLUMNS, ScanDoc.guid.label("id"))
        .join(ScanDoc, ScanDoc.doc_id == Doc.id)
        .join(Scan, Scan.guid == ScanDoc.scan_id)
        .join(Shop, Shop.latest_scan_id == Scan.guid)
        .where(Shop.shop_identifier == shop_id)
    )
    result = session.execute(query).all()
    return result


def get_doc_by_id(session: Session, doc_id: str):
    query = (
        select(*DOC_COLUMNS, ScanDoc.guid.label("id"))
        .join(ScanDoc, ScanDoc.doc_id == Doc.id)
        .where(ScanDoc.guid == doc_id)
    )
    doc = session.execute(query).first()
    if doc is None:
        raise DocNotFoundError()
    return doc


def delete_docs(session: Session, doc_ids: List[str]):
    query = delete(
        ScanDoc
    ).where(
        ScanDoc.guid.in_(doc_ids)
    )
    session.execute(query)
