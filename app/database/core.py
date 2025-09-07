from typing import Any, AsyncGenerator

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.config import config


class Base(DeclarativeBase):
    def as_dict(self, *, exclude: set[str] | None = None) -> dict[str, Any]:
        exclude_columns = set() if exclude is None else exclude
        columns_data: dict[str, Any] = {}
        for column in self.__table__.columns:
            if column.name in exclude_columns:
                continue

            value = getattr(self, column.name)

            if isinstance(value, BaseModel):
                columns_data[column.name] = value.dict()
            elif isinstance(value, list) and all(
                isinstance(item, BaseModel) for item in value
            ):
                columns_data[column.name] = [item.dict() for item in value]
            else:
                columns_data[column.name] = value
        return columns_data


engine = create_async_engine(
    config.DATABASE_URL, poolclass=NullPool, pool_pre_ping=True
)
async_session = async_sessionmaker(
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    bind=engine,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    try:
        async with async_session() as session, session.begin():
            yield session
    except:
        await session.rollback()
        raise

