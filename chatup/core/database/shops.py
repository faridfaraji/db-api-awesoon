


from sqlalchemy import delete, select
from chatup.core.exceptions import ShopNotFoundError
from chatup.model.schema.shop import NegativeKeyWord, Shop, ShopNegativeKeyWord


def get_shop_with_shopify_id(session, shop_id):
    query = select(Shop).where(Shop.shop_identifier == shop_id)
    shop = session.scalars(query).first()
    if shop is None:
        raise ShopNotFoundError
    return shop


def upsert_shop(session, shop_id, data):
    try:
        shop = get_shop_with_shopify_id(session, shop_id)
        for field in data:
            setattr(shop, field, data[field])
    except ShopNotFoundError:
        shop = Shop(**data, shop_id=shop_id)
    session.add(shop)
    return shop


def upsert_shop_negative_keyword(session, word, shop_id):
    shop = get_shop_with_shopify_id(session, shop_id)
    shop.negative_keywords.append(word)
    return shop


def delete_negative_keyword(session, word: str, shop_id: int):
    query = delete(
                ShopNegativeKeyWord
        ).where(
            ShopNegativeKeyWord.shop_id == shop_id,
            ShopNegativeKeyWord.nk_id == session.query(
                NegativeKeyWord.id
            ).filter_by(word=word).scalar()
        )
    session.execute(query)
