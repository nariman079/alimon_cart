from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, Request, Response

from src.conf.database import Base, session_context
from src.conf.settings import PRODUCTION_MODE, async_session, engine
from src.routers import cart_router


async def reinit_database() -> None:  
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    if not PRODUCTION_MODE:
        await reinit_database()
        
    yield



app = FastAPI(lifespan=lifespan)

app.include_router(prefix="/api", router=cart_router.cart_router)


@app.get("/ping")
async def ping():
    print("ping")
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

