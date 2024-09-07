import warnings
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from inteliver.storage.exceptions import CludnameNotSetException
from inteliver.users.exceptions import (
    DatabaseException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from inteliver.users.models import User
from inteliver.users.schemas import UserCreate, UserOut, UserPatch, UserPut
from inteliver.users.service import UserService


@pytest.mark.asyncio
async def test_create_user(db_session, clear_users):
    user_in = UserCreate(
        name="testuser",
        email_username="testuser@example.com",
        cloudname="test_cloudname",
        password="password123",
    )

    user_out = await UserService.create_user(db=db_session, user=user_in)
    assert isinstance(user_out, UserOut)
    assert user_out.email_username == "testuser@example.com"
    assert user_out.name == "testuser"
    assert user_out.cloudname == "test_cloudname"

    # creating the same user should raise
    with pytest.raises(UserAlreadyExistsException):
        user_out = await UserService.create_user(db=db_session, user=user_in)


@pytest.mark.asyncio
async def test_get_user_by_id(db_session, pre_existing_user):
    """Test successfully retrieving a user by their ID."""
    user_id = pre_existing_user.uid

    user_out = await UserService.get_user_by_id(db=db_session, user_id=user_id)

    assert isinstance(user_out, UserOut)
    assert user_out.uid == pre_existing_user.uid
    assert user_out.email_username == pre_existing_user.email_username
    assert user_out.name == pre_existing_user.name
    assert user_out.cloudname == pre_existing_user.cloudname


@pytest.mark.asyncio
async def test_get_user_by_id_nonexistent(db_session):
    """Test retrieving a user by a non-existent ID raises UserNotFoundException."""
    non_existent_user_id = uuid4()  # Generate a random UUID that doesn't exist

    with pytest.raises(UserNotFoundException):
        await UserService.get_user_by_id(db=db_session, user_id=non_existent_user_id)


@pytest.mark.asyncio
async def test_get_user_by_email(db_session, pre_existing_user):
    """Test retrieving a user by email."""
    user_email = pre_existing_user.email_username

    # Call the service to retrieve the user by email
    user_out = await UserService.get_user_by_email(db=db_session, email=user_email)

    # Assertions to check if the user was retrieved correctly
    assert isinstance(user_out, UserOut)
    assert user_out.email_username == pre_existing_user.email_username
    assert user_out.name == pre_existing_user.name
    assert user_out.cloudname == pre_existing_user.cloudname


@pytest.mark.asyncio
async def test_get_user_by_email_not_found(db_session, clear_users):
    """Test retrieving a user by email that does not exist."""
    non_existent_email = "nonexistent@example.com"

    # Attempt to retrieve a user that does not exist
    with pytest.raises(UserNotFoundException):
        await UserService.get_user_by_email(db=db_session, email=non_existent_email)


@pytest.mark.asyncio
async def test_get_user_by_cludname(db_session, pre_existing_user):
    """Test retrieving a user by cloudname."""
    user_cloudname = pre_existing_user.cloudname

    # Call the service to retrieve the user by cloudname
    user_out = await UserService.get_user_by_cloudname(
        db=db_session, cloudname=user_cloudname
    )

    # Assertions to check if the user was retrieved correctly
    assert isinstance(user_out, UserOut)
    assert user_out.email_username == pre_existing_user.email_username
    assert user_out.name == pre_existing_user.name
    assert user_out.cloudname == pre_existing_user.cloudname


@pytest.mark.asyncio
async def test_get_user_by_cloudname_not_found(db_session, clear_users):
    """Test retrieving a user by cloudname that does not exist."""
    non_existent_cloudname = "nonexistent_cloudname"

    # Attempt to retrieve a user that does not exist
    with pytest.raises(UserNotFoundException):
        await UserService.get_user_by_cloudname(
            db=db_session, cloudname=non_existent_cloudname
        )


@pytest.mark.asyncio
async def test_get_all_users_success(db_session: AsyncSession, create_test_users):
    """Test successfully retrieving all users with default pagination."""
    users = await UserService.get_all_users(db=db_session)

    assert isinstance(users, list)
    assert len(users) == 10  # Default limit
    assert all(isinstance(user, UserOut) for user in users)
    assert users[0].email_username == "user1@example.com"
    assert users[9].email_username == "user10@example.com"


@pytest.mark.asyncio
async def test_get_all_users_custom_pagination(
    db_session: AsyncSession, create_test_users
):
    """Test retrieving users with custom pagination."""
    users = await UserService.get_all_users(db=db_session, skip=5, limit=5)

    assert isinstance(users, list)
    assert len(users) == 5
    assert all(isinstance(user, UserOut) for user in users)
    assert users[0].email_username == "user6@example.com"
    assert users[4].email_username == "user10@example.com"


@pytest.mark.asyncio
async def test_get_all_users_exceed_available(
    db_session: AsyncSession, create_test_users
):
    """Test retrieving users when limit exceeds available users."""
    users = await UserService.get_all_users(db=db_session, skip=10, limit=10)

    assert isinstance(users, list)
    assert len(users) == 5  # Only 5 users left after skipping 10
    assert all(isinstance(user, UserOut) for user in users)
    assert users[0].email_username == "user11@example.com"
    assert users[4].email_username == "user15@example.com"


@pytest.mark.asyncio
async def test_get_all_users_empty_result(db_session: AsyncSession, create_test_users):
    """Test retrieving users when skip exceeds available users."""
    users = await UserService.get_all_users(db=db_session, skip=20, limit=10)

    assert isinstance(users, list)
    assert len(users) == 0


@pytest.mark.asyncio
async def test_get_all_users_database_exception(db_session: AsyncSession, mocker):
    """Test handling of DatabaseException."""
    mocker.patch(
        "inteliver.users.crud.UserCRUD.get_all_users",
        side_effect=DatabaseException("Database error"),
    )

    with pytest.raises(DatabaseException):
        await UserService.get_all_users(db=db_session)


@pytest.mark.asyncio
async def test_get_all_users_validation_error(db_session: AsyncSession, mocker):
    """Test handling of Pydantic ValidationError."""
    # Create a mock user with invalid data
    mock_user = User(
        uid="invalid-uid",  # Assuming uid should be a valid UUID
        name="Test User",
        email_username="invalid-email",  # Invalid email format
        cloudname="test_cloud",
        password="hashed_password",
    )

    # Patch UserCRUD.get_all_users to return our mock user
    mocker.patch(
        "inteliver.users.crud.UserCRUD.get_all_users", return_value=[mock_user]
    )

    with pytest.raises(ValidationError):
        await UserService.get_all_users(db=db_session)


@pytest.mark.asyncio
async def test_update_user_success(db_session: AsyncSession, pre_existing_user: User):
    # Arrange
    user_id = pre_existing_user.uid
    user_put = UserPut(name="Updated Name")

    # Act
    updated_user = await UserService.update_user(db_session, user_id, user_put)

    # Assert
    assert isinstance(updated_user, UserOut)
    assert updated_user.name == "Updated Name"
    assert updated_user.email_username == pre_existing_user.email_username
    assert updated_user.cloudname == pre_existing_user.cloudname


@pytest.mark.asyncio
async def test_update_user_not_found(db_session: AsyncSession):
    # Arrange
    non_existent_id = UUID("00000000-0000-0000-0000-000000000000")
    user_put = UserPut(name="Updated Name")

    # Act & Assert
    with pytest.raises(UserNotFoundException):
        await UserService.update_user(db_session, non_existent_id, user_put)


@pytest.mark.asyncio
async def test_patch_user_success(db_session: AsyncSession, pre_existing_user: User):
    # Arrange
    user_id = pre_existing_user.uid
    user_patch = UserPatch(name="Updated Name")

    # Act
    updated_user = await UserService.patch_user(db_session, user_id, user_patch)

    # Assert
    assert isinstance(updated_user, UserOut)
    assert updated_user.name == "Updated Name"
    assert updated_user.email_username == pre_existing_user.email_username
    assert updated_user.cloudname == pre_existing_user.cloudname


@pytest.mark.asyncio
async def test_patch_user_not_found(db_session: AsyncSession):
    # Arrange
    non_existent_id = UUID("00000000-0000-0000-0000-000000000000")
    user_patch = UserPatch(name="Updated Name")

    # Act & Assert
    with pytest.raises(UserNotFoundException):
        await UserService.patch_user(db_session, non_existent_id, user_patch)


@pytest.mark.asyncio
async def test_delete_user_success(db_session: AsyncSession, pre_existing_user: User):
    # Arrange
    user_id = pre_existing_user.uid

    # Act
    deleted_user = await UserService.delete_user(db_session, user_id)

    # Assert
    assert isinstance(deleted_user, UserOut)
    assert deleted_user.uid == user_id
    assert deleted_user.name == pre_existing_user.name
    assert deleted_user.email_username == pre_existing_user.email_username
    assert deleted_user.cloudname == pre_existing_user.cloudname


@pytest.mark.asyncio
async def test_delete_user_not_found(db_session: AsyncSession):
    # Arrange
    non_existent_id = uuid4()

    # Act & Assert
    with pytest.raises(UserNotFoundException):
        await UserService.delete_user(db_session, non_existent_id)


@pytest.mark.asyncio
async def test_get_cloudname_success(db_session, pre_existing_user):
    """Test retrieving cloudname by user_id."""
    user_id = pre_existing_user.uid

    # Call the service to retrieve the user by cloudname
    cloudname = await UserService.get_cloudname(db=db_session, user_id=user_id)

    # Assertions to check if the user was retrieved correctly
    assert cloudname == pre_existing_user.cloudname


@pytest.mark.asyncio
async def test_get_cloudname_non_existent_user(db_session):
    """Test retrieving cloudname by user_id."""
    non_existent_id = UUID("00000000-0000-0000-0000-000000000000")

    # Act & Assert
    with pytest.raises(CludnameNotSetException):
        await UserService.get_cloudname(db=db_session, user_id=non_existent_id)
