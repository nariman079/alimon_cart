import json
from collections import namedtuple

from src.conf.settings import redis

Product = namedtuple("Product", ["id", "name", "price"])


async def set_cache(key: str, value: dict):
    """Setting cache data"""
    value_json = json.dumps(value)
    value = await redis.set(key, value_json)
    return value


async def get_cache(key: str) -> dict:
    """Getting cache data by key"""
    value = redis.get(key)
    if not value:
        raise ValueError(f"Not product with id {key}")
    value_dict = json.loads(value)
    return value_dict


async def get_product(product_id: int) -> Product:
    product_dict = await get_cache(key=product_id)
    return Product(
        name=product_dict["name"], price=product_dict["price"], id=product_dict["id"]
    )
