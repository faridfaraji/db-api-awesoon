
from awesoon.core.database.shops import get_shop_with_identifier
from awesoon.model.schema.prompt import Prompt


def get_prompt_by_shop(session, shop_identifier):
    shop = get_shop_with_identifier(session, shop_identifier)
    return shop.prompt


def upsert_prompt_shop(session, shop_identifier, prompt):
    shop = get_shop_with_identifier(session, shop_identifier)
    prompt = Prompt(prompt=prompt)
    session.add(prompt)
    shop.prompt = prompt
