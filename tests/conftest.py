import asyncio
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from inteliver.auth.utils import get_password_hash
from inteliver.config import settings
from inteliver.users.models import User
from inteliver.users.schemas import UserCreate

# pytest.mark.asyncio(scope="session")(())

# Set the event loop policy to the default policy
# asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

# @pytest.fixture(scope="session")
# def event_loop():
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()

Base = declarative_base()
DATABASE_URL = f"postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}/{settings.postgres_db}"


@pytest_asyncio.fixture(scope="function")
async def clear_users(db_session):
    """Fixture to clear all users from the database before each test."""
    await db_session.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
    await db_session.commit()


@pytest_asyncio.fixture(scope="function")
async def db_engine():

    # Set up the asynchronous database engine
    engine = create_async_engine(DATABASE_URL, echo=False)

    # Initialize the database (create tables)
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Tear down the database (drop tables)
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine):
    # Create a new session factory using the engine provided by the db_engine fixture
    SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=db_engine, class_=AsyncSession
    )

    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def pre_existing_user(db_session):
    """Fixture to create a pre-existing user in the test database and clean up after the test."""
    user_in = UserCreate(
        name="existing_user",
        email_username="existing_user@example.com",
        cloudname="existing_cloudname",
        password="password123",
    )

    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        name=user_in.name,
        email_username=user_in.email_username,
        cloudname=user_in.cloudname,
        password=hashed_password,
    )

    db_session.add(db_user)
    await db_session.commit()
    await db_session.refresh(db_user)

    yield db_user

    # Cleanup: Delete the user after the test
    await db_session.delete(db_user)
    await db_session.commit()


@pytest_asyncio.fixture(scope="function")
async def create_test_users(db_session: AsyncSession):
    """Fixture to create multiple test users in the database."""
    users_data = [
        {
            "name": f"user{i}",
            "email_username": f"user{i}@example.com",
            "cloudname": f"cloudname{i}",
            "password": f"password{i}",
        }
        for i in range(1, 16)  # Create 15 users
    ]

    for user_data in users_data:
        hashed_password = get_password_hash(user_data["password"])
        db_user = User(
            name=user_data["name"],
            email_username=user_data["email_username"],
            cloudname=user_data["cloudname"],
            password=hashed_password,
        )
        db_session.add(db_user)

    await db_session.commit()

    yield

    # Cleanup: Delete all users after the test
    await db_session.execute(User.__table__.delete())
    await db_session.commit()


# @pytest.fixture(scope="function")
# async def client(db_session):
#     from inteliver.database.dependencies import get_db
#     from inteliver.main import app

#     async def override_get_db():
#         try:
#             yield db_session
#         finally:
#             await db_session.close()

#     app.dependency_overrides[get_db] = override_get_db

#     from fastapi.testclient import TestClient

#     with TestClient(app) as test_client:
#         yield test_client
