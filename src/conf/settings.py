import asyncio
import sys
from os import getenv
from pathlib import Path

from dotenv import load_dotenv
from redis import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

load_dotenv()


current_directory: Path = Path.cwd()

if sys.platform == "win32":  
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


PRODUCTION_MODE = True

REDIS_HOST = getenv("REDIS_HOST", 'localhost')
REDIS_PORT = getenv("REDIS_PORT", 6379)

if PRODUCTION_MODE:
    POSTGRES_USER = getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD")
    POSTGRES_DB = getenv("POSTGRES_DB")
    POSTGRES_HOST = getenv("POSTGRES_HOST")
    POSTGRES_PORT = getenv("POSTGRES_PORT")

    DB_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
else:
    DB_URL = "postgresql+asyncpg://test:test@localhost:5431/test"

print(f"POSTGRES_USER: {POSTGRES_USER}")
print(f"POSTGRES_PASSWORD: {POSTGRES_PASSWORD}")
print(f"POSTGRES_DB: {POSTGRES_DB}")
print(f"POSTGRES_HOST: {POSTGRES_HOST}")
print(f"POSTGRES_PORT: {POSTGRES_PORT}")
print(DB_URL)

engine = create_async_engine(
    DB_URL,
    pool_recycle=280,  
    echo=not PRODUCTION_MODE,
)

async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

redis = Redis(host=REDIS_HOST, port=REDIS_PORT)

ALGORITHM = getenv('ALGORITHM', 'HS256')
SECRET = getenv('SECRET_KEY', 'secret')