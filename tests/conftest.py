import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
import asyncio

from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

TEST_ENGINE = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    TEST_ENGINE,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


# Фикстура для event loop (обязательно для асинхронных тестов)
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Создаём таблицы один раз на всю сессию"""

    async def _setup():
        async with TEST_ENGINE.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(_setup())
    yield

    # Очищаем после всех тестов
    async def _teardown():
        async with TEST_ENGINE.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await TEST_ENGINE.dispose()

    asyncio.run(_teardown())


@pytest.fixture(scope="function", autouse=True)
def clean_database():
    """Очистка таблиц перед каждым тестом"""

    async def _clean():
        async with TestSessionLocal() as session:
            # Получаем все таблицы в правильном порядке (с учетом foreign keys)
            for table in reversed(Base.metadata.sorted_tables):
                await session.execute(text(f"DELETE FROM {table.name}"))
            await session.commit()

    asyncio.run(_clean())
    yield


# Клиент для тестов
@pytest.fixture(scope="function")
def client():
    """Синхронный клиент для тестов"""
    async def override_get_db():
        async with TestSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()