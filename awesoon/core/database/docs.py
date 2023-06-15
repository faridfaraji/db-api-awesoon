from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session
from awesoon.core.database.shops import get_shop_with_identifier
from awesoon.model.schema import CONNECTION_STRING_PG_VECTOR
from awesoon.model.schema.shop import Shop
from langchain.vectorstores.pgvector import EmbeddingStore, CollectionStore, PGVector, DistanceStrategy
from langchain.schema import Document


def get_shop_docs(session: Session, shop_id: int):
    query = select(
        EmbeddingStore.document, EmbeddingStore.embedding, Shop.docs_version
    ).join(
        CollectionStore, EmbeddingStore.collection_id == CollectionStore.uuid
    ).join(
        Shop, Shop.collection_id == CollectionStore.uuid
    ).where(
        Shop.shop_identifier == shop_id
    )
    result = session.execute(query).all()
    processed_result = []
    for item in result:
        processed_result.append(
            {
                "document": item[0],
                "embedding": [float(value) for value in item[1]],
                "docs_version": item[2]
            }
        )
    return processed_result


def add_shop_docs(session: Session, shop_doc: dict, shop_id: int):
    shop: Shop = get_shop_with_identifier(session, shop_id)
    embedding = shop_doc["embedding"]
    doc = shop_doc["document"]
    version = shop_doc["docs_version"]
    pre_delete_collection = False
    if shop.docs_version != version:
        pre_delete_collection = True
        shop.docs_version = version
    vector_store = PGVector(
        connection_string=CONNECTION_STRING_PG_VECTOR,
        embedding_function=None,
        collection_name=f"{shop.name}_{shop.shop_identifier}",
        distance_strategy=None,
        pre_delete_collection=pre_delete_collection
    )
    shop.collection_id = vector_store.get_collection(session).uuid
    session.add(shop)
    vector_store.add_embeddings([doc], [embedding], [{}], [None])


def get_closest_shop_doc(
        session: Session,
        embedding: List[float],
        shop_id: int,
        number_of_docs: int = 4
) -> List[Document]:
    shop: Shop = get_shop_with_identifier(session, shop_id)
    vector_store = PGVector(
        connection_string=CONNECTION_STRING_PG_VECTOR,
        embedding_function=None,
        collection_name=f"{shop.name}_{shop.shop_identifier}",
        distance_strategy=DistanceStrategy.COSINE
    )
    return vector_store.similarity_search_by_vector(embedding, k=number_of_docs)
