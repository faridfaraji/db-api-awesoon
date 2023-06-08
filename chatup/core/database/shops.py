


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
        shop = Shop(**data, shop_identifier=shop_id)
    session.add(shop)
    return shop


def upsert_shop_negative_keyword(session, word, shop_id):
    
    shop = get_shop_with_shopify_id(session, shop_id)
    new_shop_negative_keyword = ShopNegativeKeyWord(shop=shop, negative_keyword=NegativeKeyWord(word=word))
    session.add(new_shop_negative_keyword)
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


def get_keywords_for_shop(session, shop_identifier):
    query = select(NegativeKeyWord.word).join(
        ShopNegativeKeyWord, ShopNegativeKeyWord.nk_id == NegativeKeyWord.id
        ).join(
        Shop, Shop.id == ShopNegativeKeyWord.shop_id
        ).where(
            Shop.shop_identifier == shop_identifier
        )
    return session.scalars(query).all()
