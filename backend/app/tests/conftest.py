import asyncio
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.config import settings
from app.api import deps

# Use existing DB for now
TEST_DATABASE_URL = settings.DATABASE_URL

# Removed manual event_loop fixture to let pytest-asyncio handle it, or strict function scope.
# Session scope caused issues with loop mismatch.

@pytest.fixture(scope="function")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    yield engine
    await engine.dispose()

@pytest.fixture(scope="function")
async def client(test_engine) -> AsyncGenerator[AsyncClient, None]:
    async_session_factory = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with async_session_factory() as session:
            yield session

    app.dependency_overrides[deps.get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
