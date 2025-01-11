from typing import Annotated

import jwt
from fastapi import Header, Path


async def get_or_validate_access_data(raw_token: str) -> dict:
    """Проверка токена доступа"""
    try:
        payload = jwt.decode(raw_token, "secret", algorithms=["HS256"])
        print(payload)
        return payload
    except jwt.ExpiredSignatureError:
        return {"valid": False, "reason": "Token expired"}
    except jwt.InvalidTokenError:
        return {"valid": False, "reason": "Invalid token"}


async def get_user(token: Header) -> int:
    """Получение пользователя"""

    access_data = await get_or_validate_access_data(token)
    return access_data["user_id"]


async def get_cart(cart_id: Annotated[int, Path()]) -> int:
    return cart_id
