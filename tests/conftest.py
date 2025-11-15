import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.workers.celery_app import celery_app


# Create a new database engine for testing
os.environ["SQLALCHEMY_DATABASE_URL"]= "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(os.environ["SQLALCHEMY_DATABASE_URL"], echo=False, future=True)
TestingSessionLocal = sessionmaker(
    bind = test_engine, class_ = AsyncSession, expire_on_commit = False
)

async def init_test_db() -> None:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_test_db() -> None:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Override the get_db dependency to use the testing database session

@pytest.fixture(name ="db_session", scope = "function")
async def db_session_fixture() -> AsyncGenerator[AsyncSession, None]:
    await init_test_db()
    async with TestingSessionLocal() as session:
        yield session
    await drop_test_db()

@pytest.fixture(name = "client", scope = "function")
def client_fixture(db_session: AsyncSession) -> Generator[TestClient, None, None]:
    """FastAPI TestClient with DB dependency overridden"""

    async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = get_test_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# JWT token for auth-protected endpoints
@pytest.fixture
def auth_token() -> str:
    """Generate a short-lived JWT that the API accepts."""
    payload = {"sub": "test-user", "scopes": ["notifications"]}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm = "HS256")

@pytest.fixture
def auth_headers(auth_token: str) -> dict:
    """Headers including the JWT for authentication."""
    return {"Authorization": f"Bearer {auth_token}"}


# Celery - run tasks **synchronously** during tests
@pytest.fixture(autouse=True)
def celery_eager(celery_app):
    """Force celery to execute tasks eagerly for tests."""
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    yield
    celery_app.conf.task_always_eager = False
    celery_app.conf.task_eager_propagates = False


# Helper - create a notification payload
@pytest.fixture
def notification_payload():
    return {
        "event_type": "signup",
        "channel": "email",
        "recipient": "test@example.com",
        "content": "Welcome to the platform!"
    }    