import asyncio
import os
from io import BytesIO
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi import UploadFile
from httpx import AsyncClient
from minio import Minio, S3Error
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from inteliver.auth.schemas import Token
from inteliver.auth.service import AuthService
from inteliver.auth.utils import get_password_hash
from inteliver.config import settings
from inteliver.database.dependencies import get_db
from inteliver.main import app
from inteliver.storage.service import StorageService
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


@pytest_asyncio.fixture(scope="module")
async def minio_client():
    return Minio(
        settings.minio_host,
        access_key=settings.minio_root_user,
        secret_key=settings.minio_root_password,
        secure=settings.minio_secure,
    )


@pytest_asyncio.fixture(scope="function")
async def cleanup_minio(minio_client, pre_existing_user):
    yield
    # Clean up the bucket after each test
    try:
        objects = minio_client.list_objects(pre_existing_user.cloudname, recursive=True)
        for obj in objects:
            minio_client.remove_object(pre_existing_user.cloudname, obj.object_name)
        minio_client.remove_bucket(pre_existing_user.cloudname)
    except S3Error:
        pass


@pytest_asyncio.fixture(scope="function")
async def setup_minio_data(minio_client, pre_existing_user):
    # Path to the sample test image
    filepath = "tests/assets/images/jpg_test_image.jpeg"

    # Ensure the file exists
    assert os.path.exists(filepath), f"Test image not found at {filepath}"

    # Read the image file
    with open(filepath, "rb") as image_file:
        image_data = image_file.read()

    bucket_name = pre_existing_user.cloudname
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

    # Upload the image 10 times with different names
    for i in range(10):
        object_name = f"test_image_{i+1}.jpg"
        minio_client.put_object(
            bucket_name,
            object_name,
            data=BytesIO(image_data),
            length=len(image_data),
            content_type="image/jpeg",
        )

    yield

    # Clean up after test
    objects = minio_client.list_objects(bucket_name, recursive=True)
    for obj in objects:
        minio_client.remove_object(bucket_name, obj.object_name)
    minio_client.remove_bucket(bucket_name)


@pytest_asyncio.fixture(scope="function")
async def test_image_file():
    # Prepare test data
    filepath = "tests/assets/images/jpg_test_image.jpeg"
    with open(filepath, "rb") as image_file:
        file = UploadFile(
            filename="jpg_test_image.jpg", file=BytesIO(image_file.read())
        )
    yield file


@pytest_asyncio.fixture
async def uploaded_image(db_session, pre_existing_user: User):
    filepath = "tests/assets/images/jpg_test_image.jpeg"

    with open(filepath, "rb") as image_file:
        file_content = image_file.read()

    file = UploadFile(
        filename="jpg_test_image.jpg",
        file=BytesIO(file_content),
        size=len(file_content),
    )
    # Upload the image
    uploaded = await StorageService.upload_image(
        db_session, pre_existing_user.uid, file
    )

    yield uploaded


@pytest_asyncio.fixture(scope="function")
async def pre_existing_admin(db_session):
    """Fixture to create a pre-existing admin user in the test database and clean up after the test."""
    admin_in = UserCreate(
        name="admin_user",
        email_username="admin@example.com",
        cloudname="admincloudname",
        password="adminpassword123",
    )

    hashed_password = get_password_hash(admin_in.password)
    db_admin = User(
        name=admin_in.name,
        email_username=admin_in.email_username,
        cloudname=admin_in.cloudname,
        password=hashed_password,
        role="admin",  # Set the role to admin
    )

    db_session.add(db_admin)
    await db_session.commit()
    await db_session.refresh(db_admin)

    yield db_admin

    # Cleanup: Delete admin and all other users created after the test
    await db_session.execute(User.__table__.delete())
    await db_session.commit()


@pytest_asyncio.fixture(scope="function")
async def user_create_data(db_session: AsyncSession):
    yield UserCreate(
        email_username="newuser@example.com",
        password="newpassword123",
        name="New User",
        cloudname="newuser",
    )
    # Cleanup: Delete all users after the test
    await db_session.execute(User.__table__.delete())
    await db_session.commit()


@pytest_asyncio.fixture(scope="function")
async def pre_existing_user(db_session):
    """Fixture to create a pre-existing user in the test database and clean up after the test."""
    user_in = UserCreate(
        name="existing_user",
        email_username="existing_user@example.com",
        cloudname="existingcloudname",
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
async def pre_existing_user_second(db_session):
    """Fixture to create a second pre-existing user in the test database and clean up after the test."""
    user_in = UserCreate(
        name="existing_user_second",
        email_username="existing_user_second@example.com",
        cloudname="existingcloudnamesecond",
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


@pytest_asyncio.fixture(scope="function")
async def test_app(db_session):
    async def override_get_db():
        try:
            yield db_session
        finally:
            await db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield app
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def test_client(test_app):
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def auth_token(pre_existing_user: User):
    """Fixture to generate a JWT token for the pre-existing user."""
    access_token = AuthService.create_access_token(
        data={
            "sub": str(pre_existing_user.uid),
            "username": pre_existing_user.email_username,
            "role": pre_existing_user.role,
        }
    )
    return Token(access_token=access_token, token_type="bearer")


@pytest_asyncio.fixture(scope="function")
async def auth_token_admin(pre_existing_admin: User):
    """Fixture to generate a JWT token for the pre-existing user."""
    access_token = AuthService.create_access_token(
        data={
            "sub": str(pre_existing_admin.uid),
            "username": pre_existing_admin.email_username,
            "role": pre_existing_admin.role,
        }
    )
    return Token(access_token=access_token, token_type="bearer")
