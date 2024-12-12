import os
from dotenv import load_dotenv

load_dotenv()

from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    async_sessionmaker,
    create_async_engine, AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=True)
new_session = async_sessionmaker(engine, class_= AsyncSession, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)