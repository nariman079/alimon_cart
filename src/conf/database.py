from __future__ import annotations

from collections.abc import Sequence
from contextvars import ContextVar
from typing import Any, Self

from sqlalchemy import MetaData, Row, Select, func, select
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.orm import DeclarativeBase

session_context: ContextVar[AsyncSession | None] = ContextVar("session", default=None)


class DBController:
    @property
    def session(self) -> AsyncSession:
        """Получение сессии из контекстных переменных"""
        session = session_context.get()
        if session is None:
            raise ValueError("Сессия не запущена")
        return session

    async def get_first_row(self, stmt: Select[Any]) -> Row[Any]:
        """Получение первой строку"""
        return (await self.session.execute(stmt)).first()

    async def get_first(self, stmt: Select[Any]) -> Any | None:
        """Получение первого объекта из результата"""
        return (await self.session.execute(stmt)).scalars().first()

    async def is_exists(self, stmt: Select[Any]) -> bool:
        """Проверка на существование объекта"""
        return (await self.get_first(stmt)) is not None

    async def get_count(self, stmt: Select[tuple[int]]) -> int:
        """Подсчет количества записей"""
        return (await self.session.execute(stmt)).scalar_one()

    async def get_all(self, stmt: Select[Any]) -> Sequence[Any]:
        """Получение всех объектов"""
        return (await self.session.execute(stmt)).scalars().all()

    async def get_paginated(
        self, stmt: Select[Any], offset: int, limit: int
    ) -> Sequence[Any]:
        return await self.get_all(stmt.offset(offset).limit(limit))


db: DBController = DBController()


class MappingBase:
    @classmethod
    async def create(cls, **kwargs) -> Self:
        entry = cls(**kwargs)  # type: ignore
        db.session.add(entry)
        await db.session.flush()
        return entry

    @classmethod
    def select_by_kwargs(cls, *order_by: Any, **kwargs: Any) -> Select[tuple[Self]]:
        if len(order_by) == 0:
            return select(cls).filter_by(**kwargs)
        return select(cls).filter_by(**kwargs).order_by(*order_by)

    @classmethod
    async def find_first_by_id(cls, *keys: Any) -> Self | None:
        return await db.session.get(cls, *keys)

    @classmethod
    async def find_first_by_kwargs(cls, *order_by: Any, **kwargs: Any) -> Self | None:
        return await db.get_first(cls.select_by_kwargs(*order_by, **kwargs))

    @classmethod
    async def find_all_by_kwargs(cls, *order_by: Any, **kwargs: Any) -> Sequence[Self]:
        return await db.get_all(cls.select_by_kwargs(*order_by, **kwargs))

    @classmethod
    async def find_paginated_by_kwargs(
        cls, offset: int, limit: int, *order_by: Any, **kwargs: Any
    ) -> Sequence[Self]:
        return await db.get_paginated(
            cls.select_by_kwargs(*order_by, **kwargs), offset, limit
        )

    @classmethod
    async def count_by_kwargs(cls, *expressions: Any, **kwargs: Any) -> int:
        return await db.get_count(
            select(func.count(*expressions, **kwargs)).filter_by(**kwargs)
        )

    async def update(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)
        await db.session.flush()

    async def delete(self):
        await db.session.delete(self)
        await db.session.flush()


convention = {
    "ix": "ix_%(column_0_label)s",  # noqa: WPS323
    "uq": "uq_%(table_name)s_%(column_0_name)s",  # noqa: WPS323
    "ck": "ck_%(table_name)s_%(constraint_name)s",  # noqa: WPS323
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # noqa: WPS323
    "pk": "pk_%(table_name)s",  # noqa: WPS323
}


db_meta = MetaData(naming_convention=convention)


class Base(AsyncAttrs, DeclarativeBase, MappingBase):
    __tablename__: str
    __abstract__: bool

    metadata = db_meta
