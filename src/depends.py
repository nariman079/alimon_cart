from typing import Annotated

import jwt
from fastapi import HTTPException, Path, Request

from src.conf.settings import ALGORITHM, SECRET
from src.schemas import AuthUser


async def get_or_validate_access_data(raw_token: str) -> dict:
    """Проверка токена доступа"""
    try:
        payload = jwt.decode(raw_token, SECRET, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401,  detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401,  detail="Token invalid") 


async def get_user(request: Request) -> AuthUser:
    """Получение пользователя"""
    token = request.headers.get('Authorization').split(' ')[-1]

    access_data = await get_or_validate_access_data(token)
    auth_user = AuthUser(user_id=access_data['user_id'])
    return auth_user


async def get_cart(cart_id: Annotated[int, Path()]) -> int:
    return cart_id
