from sqlalchemy import and_, delete, select
from awesoon.core.exceptions import ShopNotFoundError
from awesoon.model.schema.shop import NegativeKeyWord, Shop, ShopNegativeKeyWord, ShopifyApp, ShopifyAppInstallation


def get_shopify_apps(session, args):
    query = select(ShopifyApp)
    if args["app_name"]:
        query = query.filter(ShopifyApp.app_name == args["app_name"])
    return session.scalars(query).all()


def get_shopify_app_with_name(session, app_name):
    query = select(ShopifyApp)
    query = query.filter(ShopifyApp.app_name == app_name)
    return session.scalars(query).first()


def get_all_shopify_app_installations(session, shop_identifier, args):
    query = (
        select(ShopifyApp.app_name, ShopifyAppInstallation.access_token, Shop.shop_url)
        .join(Shop, ShopifyAppInstallation.shop_id == Shop.id)
        .join(ShopifyApp, ShopifyApp.app_client_id == ShopifyAppInstallation.app_id)
        .where(Shop.shop_identifier == shop_identifier)
    )
    if args["app_name"]:
        query = query.filter(ShopifyApp.app_name == args["app_name"])
    return session.execute(query).all()
