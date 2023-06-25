from typing import List
from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from awesoon.core.database.scans import get_scan_object_by_scan_id
from awesoon.core.database.shops import get_shop_with_identifier
from awesoon.core.exceptions import DocNotFoundError
from awesoon.model.schema import CONNECTION_STRING_PG_VECTOR
from awesoon.model.schema.doc import Doc
from awesoon.model.schema.scan import Scan, ScanDoc
from awesoon.model.schema.shop import Shop
from langchain.vectorstores.pgvector import EmbeddingStore, CollectionStore, PGVector, DistanceStrategy
from langchain.schema import Document


# def get_shop_docs(session: Session, shop_id: int, args: dict):
#     query = (
#         select(EmbeddingStore.document, EmbeddingStore.embedding, Shop.docs_version)
#         .join(CollectionStore, EmbeddingStore.collection_id == CollectionStore.uuid)
#         .join(Shop, Shop.collection_id == CollectionStore.uuid)
#         .where(Shop.shop_identifier == shop_id)
#     )
#     result = session.execute(query).all()
#     show_embedding = args["show_embedding"]
#     processed_result = []
#     for item in result:
#         doc = {"document": item[0], "docs_version": item[2]}
#         if show_embedding:
#             doc["embedding"] = [float(value) for value in item[1]]
#         processed_result.append(doc)
#     return processed_result


def add_shop_docs(session: Session, shop_doc: dict, shop_id: int):
    shop: Shop = get_shop_with_identifier(session, shop_id)
    embedding = shop_doc["embedding"]
    doc = shop_doc["document"]
    version = shop_doc["docs_version"]
    pre_delete_collection = False
    if shop.docs_version != version:
        pre_delete_collection = True
        shop.docs_version = version
        shop.collection_id = None
        session.commit()
    vector_store = PGVector(
        connection_string=CONNECTION_STRING_PG_VECTOR,
        embedding_function=None,
        collection_name=f"{shop.shop_name}_{shop.shop_identifier}",
        distance_strategy=None,
        pre_delete_collection=pre_delete_collection,
    )
    shop.collection_id = vector_store.get_collection(session).uuid
    session.add(shop)
    session.commit()
    vector_store.add_embeddings([doc], [embedding], [{}], [None])


def get_closest_shop_doc(
    session: Session, embedding: List[float], shop_id: int, number_of_docs: int = 4
) -> List[Document]:
    shop: Shop = get_shop_with_identifier(session, shop_id)
    vector_store = PGVector(
        connection_string=CONNECTION_STRING_PG_VECTOR,
        embedding_function=None,
        collection_name=f"{shop.shop_name}_{shop.shop_identifier}",
        distance_strategy=DistanceStrategy.COSINE,
    )
    return vector_store.similarity_search_by_vector(embedding, k=number_of_docs)


def add_scan_doc(session: Session, doc: dict, scan_id: str):
    scan = get_scan_object_by_scan_id(session, scan_id)
    doc = Doc(**doc)
    session.add(doc)
    session.flush()
    scan_doc = ScanDoc(scan_id=scan.guid, doc_id=doc.id)
    session.add(scan_doc)


def get_scan_docs(session: Session, scan_id: str):
    query = (
        select(Doc.doc_type, Doc.doc_identifier, Doc.hash, Doc.embedding, Doc.document, ScanDoc.guid.label("id"))
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


def get_shop_docs(session: Session, shop_id: int, args: dict):
    query = (
        select(Doc)
        .join(ScanDoc, ScanDoc.doc_id == Doc.id)
        .join(Scan, Scan.guid == ScanDoc.scan_id)
        .join(Shop, Shop.latest_scan_id == Scan.guid)
        .where(Shop.shop_identifier == shop_id)
    )
    result = session.scalars(query).all()
    return result


def get_doc_by_id(session: Session, doc_id: str):
    query = (
        select(Doc.doc_type, Doc.doc_identifier, Doc.hash, Doc.embedding, Doc.document, ScanDoc.guid.label("id"))
        .join(ScanDoc, ScanDoc.doc_id == Doc.id)
        .where(ScanDoc.guid == doc_id)
    )
    doc = session.execute(query).first()
    if doc is None:
        raise DocNotFoundError()
    return doc


def delete_doc(session: Session, doc_id: str):
    query = delete(
        ScanDoc
    ).where(
        ScanDoc.guid == doc_id
    )
    session.execute(query)
