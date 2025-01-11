from typing import Callable, Awaitable
from fastapi import FastAPI, Request, Response

from src.routers import cart_router
from src.conf.settings import async_session
from src.conf.database import session_context

app = FastAPI()

app.include_router(
    prefix='/api',
    router=cart_router.cart_router
)

@app.get('/ping')
async def ping():
    print('ping')
    return "pong"


@app.middleware("http")
async def database_session_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Setup database session"""
    async with async_session.begin() as session:
        session_context.set(session)
        return await call_next(request)