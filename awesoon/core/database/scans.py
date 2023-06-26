from typing import List

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from awesoon.core.database.shops import get_shop_with_identifier
from awesoon.core.exceptions import ScanNotFoundError
from awesoon.model.schema.doc import Doc
from awesoon.model.schema.scan import Scan, ScanDoc
from awesoon.model.schema.shop import Shop

SCAN_COLUMNS = [c.label("id") if c.name == "guid"
                else c for c in Scan.__table__.c if c.name != "shop_id"]


def get_scan_object_by_scan_id(session: Session, scan_id: str):
    query = select(
        Scan
    ).join(Shop, Shop.id == Scan.shop_id).where(Scan.guid == scan_id)
    scan = session.scalars(query).first()
    if scan is None:
        raise ScanNotFoundError
    return scan


def get_scans(session: Session) -> List[List[str]]:
    """returns all scans

    Args:
        session (Session): sql session

    Returns:
        list of strings: returns all of the scans
    """
    query = select(
        *SCAN_COLUMNS, Shop.shop_identifier.label("shop_id")
    ).join(Shop, Shop.id == Scan.shop_id)
    return session.execute(query).all()


def get_scans_with_shop_id(session: Session, shop_id: int):
    """returns all of the scans for a shop

    Args:
        session (Session): sql session
        shop_id (int): shop identifier

    Returns:
        list of strings: returns all of the scans for a shop
    """
    query = select(
        *SCAN_COLUMNS, Shop.shop_identifier.label("shop_id")
    ).join(Shop, Shop.id == Scan.shop_id).where(Shop.shop_identifier == shop_id)
    return session.execute(query).all()


def get_scan_by_id(session: Session, scan_id: int):
    """returns scan with id

    Args:
        session (Session): sql session
        scan_id (int): scan id

    Returns:
        list of strings: returns scan with id
    """
    query = select(
        *SCAN_COLUMNS, Shop.shop_identifier.label("shop_id")
    ).join(Shop, Shop.id == Scan.shop_id).where(Scan.guid == scan_id)
    scan = session.execute(query).first()
    if scan is None:
        raise ScanNotFoundError
    return scan


def update_scan(session: Session, scan_id: str,  scan_data: dict):
    """updates a scan object

    Args:
        session (Session): sql session
        scan_data (dict): scan_data
    """
    try:
        shop_identifier = scan_data.pop("shop_id")
        shop = get_shop_with_identifier(session, shop_identifier)
        scan = get_scan_object_by_scan_id(session, scan_id)
        for field in scan_data:
            setattr(scan, field, scan_data[field])
        scan.shop_id = shop.id
    except ScanNotFoundError:
        scan = Scan(**scan_data)
    scan.shop_id = shop.id
    session.add(scan)


def init_scan_with_docs(session: Session, shop_id: int, scan: Scan):
    query = (
        select(Doc)
        .join(ScanDoc, ScanDoc.doc_id == Doc.id)
        .join(Scan, Scan.guid == ScanDoc.scan_id)
        .join(Shop, Shop.latest_scan_id == Scan.guid)
        .where(Shop.shop_identifier == shop_id)
    )
    docs = session.scalars(query).all()
    for doc in docs:
        session.add(ScanDoc(scan_id=scan.guid, doc_id=doc.id))


def add_scan(session: Session, scan_data: dict):
    """adds a scan

    Args:
        session (Session): sql session
        scan_data (dict): scan_data to be added
    """
    shop_identifier = scan_data.pop("shop_id")
    shop = get_shop_with_identifier(session, shop_identifier)
    scan = Scan(**scan_data, shop_id=shop.id)
    session.add(scan)
    session.flush()
    init_scan_with_docs(session, shop_identifier, scan)
    shop.latest_scan_id = scan.guid
    session.add(shop)
    return scan


def update_scan_status(session: Session, scan_id: str, status: str):
    """updates the status of a scan with id of scan_id

    Args:
        session (Session): sql session
        scan_id (int): the scan_id of the scan to update
        status (str): the new scan status
    """
    stmt = update(Scan).where(Scan.guid == scan_id).values(status=status)
    session.execute(stmt)
