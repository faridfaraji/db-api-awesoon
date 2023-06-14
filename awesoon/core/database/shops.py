
from sqlalchemy import and_, delete, select
from awesoon.core.exceptions import ShopNotFoundError
from awesoon.model.schema.shop import NegativeKeyWord, Shop, ShopNegativeKeyWord


def get_shop_with_identifier(session, shop_identifier: int) -> Shop:
    query = select(Shop).where(Shop.shop_identifier == shop_identifier)
    shop = session.scalars(query).first()
    if shop is None:
        raise ShopNotFoundError
    return shop


def upsert_shop(session, shop_identifier: int, data: dict):
    try:
        shop = get_shop_with_identifier(session, shop_identifier)
        for field in data:
            setattr(shop, field, data[field])
    except ShopNotFoundError:
        shop = Shop(**data, shop_identifier=shop_identifier)
    session.add(shop)
    return shop


def upsert_keyword(session, word: str):
    query = select(NegativeKeyWord).where(NegativeKeyWord.word == word)
    result = session.scalars(query).first()
    if result:
        return result
    else:
        return NegativeKeyWord(word=word)


def upsert_shop_negative_keyword(session, word: str, shop_identifier: int):
    shop = get_shop_with_identifier(session, shop_identifier)
    session.add(upsert_keyword(session, word))
    query = select(ShopNegativeKeyWord).where(
        and_(ShopNegativeKeyWord.negative_keyword == word), (ShopNegativeKeyWord.shop_id == shop.id))
    result = session.scalars(query).first()
    if not result:
        new_shop_negative_keyword = ShopNegativeKeyWord(shop_id=shop.id, negative_keyword=word)
        session.add(new_shop_negative_keyword)
    return shop


def delete_negative_keyword(session, word: str, shop_identifier: int):
    shop = get_shop_with_identifier(session, shop_identifier)
    query = delete(ShopNegativeKeyWord).where(and_(
            ShopNegativeKeyWord.shop_id == shop.id
        ),
        (
            ShopNegativeKeyWord.negative_keyword == word
        )
    )
    session.execute(query)


def get_keywords_for_shop(session, shop_identifier: int):
    shop = get_shop_with_identifier(session, shop_identifier)
    result = []
    for shopKw in shop.negative_keywords:
        result.append(shopKw.negative_keyword)
    return result
