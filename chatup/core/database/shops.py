


from sqlalchemy import select
from chatup.core.exceptions import ShopNotFoundError
from chatup.model.schema.shop import Shop


def get_shop_with_shopify_id(session, shop_id):
    query = select(Shop).where(Shop.shop_id == shop_id)
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
