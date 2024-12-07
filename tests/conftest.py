import asyncio

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from main import app
from src.auth.models import User
from src.auth.pass_utils import get_password_hash
from config.db import engine, Base, get_db
from config.general import settings

TEST_DB_URL = settings.database_test_url
engine = create_async_engine(TEST_DB_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    autocommit=False, autoflash=False, bind=engine, class_=AsyncSession
)


@pytest_asyncio.fixture(scope="function")
async def setup_db():
    async with engine.begin() as conn:
        # Drop all tables
        await conn.run_sync(Base.metadata.drop_all)
        # Create tables
        await conn.run_sync(Base.metadata.create_all)

    yield
    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session(setup_db):
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
def override_get_db(db_session):
    async def _get_db():
        async with db_session as session:
            yield session

        app.dependency_overrides[get_db] = _get_db()
        yield
        app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def user_password(faker):
    return faker.password()


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session, faker, user_password):
    hashed_password = get_password_hash(user_password)
    user = User(
        username=faker.username(),
        email=faker.email(),
        password_hashed=hashed_password,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)  # To get the ID from the db
    return user
