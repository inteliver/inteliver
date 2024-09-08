from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient

from inteliver.auth.schemas import Token
from inteliver.auth.service import AuthService
from inteliver.config import settings
from inteliver.users.exceptions import (
    DatabaseException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from inteliver.users.models import User
from inteliver.users.schemas import UserCreate, UserPatch, UserPut

# Test scenarios for create user
# Endpoint POST /users/


@pytest.mark.asyncio
async def test_create_new_user_success(
    test_client: AsyncClient, auth_token_admin: Token, pre_existing_admin: User
):
    new_user_data = UserCreate(
        email_username="newuser@example.com",
        password="newpassword123",
        name="New User",
        cloudname="newuser",
    )

    response = await test_client.post(
        f"{settings.api_prefix}/users/",
        json=new_user_data.model_dump(),
        headers={"Authorization": f"Bearer {auth_token_admin.access_token}"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    created_user = response.json()
    assert created_user["email_username"] == new_user_data.email_username
    assert created_user["name"] == new_user_data.name
    assert created_user["cloudname"] == new_user_data.cloudname
    assert "uid" in created_user


@pytest.mark.asyncio
async def test_create_new_user_already_exists(
    test_client: AsyncClient, auth_token_admin: Token, pre_existing_admin: User, mocker
):
    mocker.patch(
        "inteliver.users.service.UserService.create_user",
        side_effect=UserAlreadyExistsException("User already exists"),
    )

    new_user_data = UserCreate(
        email_username="existing@example.com",
        password="password123",
        name="Existing User",
        cloudname="existinguser",
    )

    response = await test_client.post(
        f"{settings.api_prefix}/users/",
        json=new_user_data.model_dump(),
        headers={"Authorization": f"Bearer {auth_token_admin.access_token}"},
    )

    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_create_new_user_unauthorized(test_client: AsyncClient):
    new_user_data = UserCreate(
        email_username="newuser@example.com",
        password="newpassword123",
        name="New User",
        cloudname="newuser",
    )

    response = await test_client.post(
        f"{settings.api_prefix}/users/", json=new_user_data.model_dump()
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_create_new_user_insufficient_role(
    test_client: AsyncClient, auth_token: Token
):
    new_user_data = UserCreate(
        email_username="newuser@example.com",
        password="newpassword123",
        name="New User",
        cloudname="newuser",
    )

    response = await test_client.post(
        f"{settings.api_prefix}/users/",
        json=new_user_data.model_dump(),
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_create_new_user_database_exception(
    test_client: AsyncClient, auth_token_admin: Token, mocker
):
    mocker.patch(
        "inteliver.users.service.UserService.create_user",
        side_effect=DatabaseException("Database error"),
    )

    new_user_data = UserCreate(
        email_username="newuser@example.com",
        password="newpassword123",
        name="New User",
        cloudname="newuser",
    )

    response = await test_client.post(
        f"{settings.api_prefix}/users/",
        json=new_user_data.model_dump(),
        headers={"Authorization": f"Bearer {auth_token_admin.access_token}"},
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_create_new_user_general_exception(
    test_client: AsyncClient, auth_token_admin: Token, mocker
):
    mocker.patch(
        "inteliver.users.service.UserService.create_user",
        side_effect=Exception("Unexpected error"),
    )

    new_user_data = UserCreate(
        email_username="newuser@example.com",
        password="newpassword123",
        name="New User",
        cloudname="newuser",
    )

    response = await test_client.post(
        f"{settings.api_prefix}/users/",
        json=new_user_data.model_dump(),
        headers={"Authorization": f"Bearer {auth_token_admin.access_token}"},
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


# Test scenarios for get user by id
# Endpoint GET /users/{user_id}


@pytest.mark.asyncio
async def test_get_user_by_id_success(
    test_client: AsyncClient, auth_token_admin: Token, pre_existing_user: User
):
    response = await test_client.get(
        f"{settings.api_prefix}/users/{pre_existing_user.uid}",
        headers={"Authorization": f"Bearer {auth_token_admin.access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    user_data = response.json()
    assert user_data["uid"] == str(pre_existing_user.uid)
    assert user_data["email_username"] == pre_existing_user.email_username
    assert user_data["name"] == pre_existing_user.name
    assert user_data["cloudname"] == pre_existing_user.cloudname


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(
    test_client: AsyncClient, auth_token_admin: Token, pre_existing_user: User, mocker
):
    non_existent_id = uuid4()
    mocker.patch(
        "inteliver.users.service.UserService.get_user_by_id",
        side_effect=UserNotFoundException("User not found"),
    )

    response = await test_client.get(
        f"{settings.api_prefix}/users/{non_existent_id}",
        headers={"Authorization": f"Bearer {auth_token_admin.access_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_user_by_id_unauthorized(test_client: AsyncClient):
    random_id = uuid4()
    response = await test_client.get(f"{settings.api_prefix}/users/{random_id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_user_by_id_insufficient_permission(
    test_client: AsyncClient,
    auth_token: Token,
    pre_existing_user: User,
    pre_existing_user_second: User,
):
    """Test a scenario that a user would request another user info"""
    # accessing second user using the credentials of the first user
    response = await test_client.get(
        f"{settings.api_prefix}/users/{pre_existing_user_second.uid}",
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_user_by_id_database_exception(
    test_client: AsyncClient,
    auth_token_admin: Token,
    pre_existing_user: User,
    mocker,
):
    mocker.patch(
        "inteliver.users.service.UserService.get_user_by_id",
        side_effect=DatabaseException("Database error"),
    )

    response = await test_client.get(
        f"{settings.api_prefix}/users/{pre_existing_user.uid}",
        headers={"Authorization": f"Bearer {auth_token_admin.access_token}"},
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_get_user_by_id_general_exception(
    test_client: AsyncClient,
    auth_token_admin: Token,
    pre_existing_user: User,
    mocker,
):
    mocker.patch(
        "inteliver.users.service.UserService.get_user_by_id",
        side_effect=Exception("Unexpected error"),
    )

    response = await test_client.get(
        f"{settings.api_prefix}/users/{pre_existing_user.uid}",
        headers={"Authorization": f"Bearer {auth_token_admin.access_token}"},
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


# Test scenarios for get user by email
# Endpoint GET /users/by-email/?email=email@example.com


@pytest.mark.asyncio
async def test_get_user_by_email_success(
    test_client: AsyncClient,
    auth_token_admin: Token,
    pre_existing_user: User,
):
    response = await test_client.get(
        f"{settings.api_prefix}/users/by-email/?email={pre_existing_user.email_username}",
        headers={"Authorization": f"Bearer {auth_token_admin.access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    user_data = response.json()
    assert user_data["email_username"] == pre_existing_user.email_username
    assert user_data["name"] == pre_existing_user.name
    assert user_data["cloudname"] == pre_existing_user.cloudname


@pytest.mark.asyncio
async def test_get_user_by_email_not_found(
    test_client: AsyncClient, auth_token_admin: Token, mocker
):
    non_existent_email = "nonexistent@example.com"

    response = await test_client.get(
        f"{settings.api_prefix}/users/by-email/?email={non_existent_email}",
        headers={"Authorization": f"Bearer {auth_token_admin.access_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_user_by_email_unauthorized(test_client: AsyncClient):
    response = await test_client.get(
        f"{settings.api_prefix}/users/by-email/?email=test@example.com"
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_user_by_email_insufficient_permission(
    test_client: AsyncClient, auth_token: Token, mocker
):
    not_current_user_email = "not_current_user_email@example.com"

    response = await test_client.get(
        f"{settings.api_prefix}/users/by-email/?email={not_current_user_email}",
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_user_by_email_database_exception(
    test_client: AsyncClient,
    auth_token: Token,
    pre_existing_user: User,
    mocker,
):
    mocker.patch(
        "inteliver.users.service.UserService.get_user_by_email",
        side_effect=DatabaseException("Database error"),
    )

    response = await test_client.get(
        f"{settings.api_prefix}/users/by-email/?email={pre_existing_user.email_username}",
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_get_user_by_email_general_exception(
    test_client: AsyncClient,
    auth_token_admin: Token,
    pre_existing_user: User,
    mocker,
):
    mocker.patch(
        "inteliver.users.service.UserService.get_user_by_email",
        side_effect=Exception("Unexpected error"),
    )

    response = await test_client.get(
        f"{settings.api_prefix}/users/by-email/?email={pre_existing_user.email_username}",
        headers={"Authorization": f"Bearer {auth_token_admin.access_token}"},
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_get_user_by_email_invalid_email(
    test_client: AsyncClient,
    auth_token_admin: Token,
):
    invalid_email = "invalid_email"
    response = await test_client.get(
        f"{settings.api_prefix}/users/by-email/?email={invalid_email}",
        headers={"Authorization": f"Bearer {auth_token_admin.access_token}"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# Test scenarios for get all users
# Endpoint GET /users/


@pytest.mark.asyncio
async def test_get_all_users_success(
    test_client: AsyncClient,
    auth_token_admin: Token,
    pre_existing_user: User,
):
    response = await test_client.get(
        f"{settings.api_prefix}/users/",
        headers={"Authorization": f"Bearer {auth_token_admin.access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    users_data = response.json()
    assert isinstance(users_data, list)
    assert len(users_data) > 0


@pytest.mark.asyncio
async def test_get_all_users_unauthorized(test_client: AsyncClient):
    response = await test_client.get(f"{settings.api_prefix}/users/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_all_users_insufficient_permission(
    test_client: AsyncClient, auth_token: Token
):
    response = await test_client.get(
        f"{settings.api_prefix}/users/",
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_all_users_database_exception(
    test_client: AsyncClient, auth_token_admin: Token, mocker
):
    mocker.patch(
        "inteliver.users.service.UserService.get_all_users",
        side_effect=DatabaseException("Database error"),
    )

    response = await test_client.get(
        f"{settings.api_prefix}/users/",
        headers={"Authorization": f"Bearer {auth_token_admin.access_token}"},
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_get_all_users_general_exception(
    test_client: AsyncClient,
    auth_token_admin: Token,
    mocker,
):
    mocker.patch(
        "inteliver.users.service.UserService.get_all_users",
        side_effect=Exception("Unexpected error"),
    )

    response = await test_client.get(
        f"{settings.api_prefix}/users/",
        headers={"Authorization": f"Bearer {auth_token_admin.access_token}"},
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


# Test scenarios for update user by id
# Endpoint put /users/


@pytest.mark.asyncio
async def test_update_user_by_id_success(
    test_client: AsyncClient, auth_token: Token, pre_existing_user: User
):
    updated_user_data = UserPut(
        name="Updated Name",
    )

    response = await test_client.put(
        f"{settings.api_prefix}/users/{pre_existing_user.uid}",
        json=updated_user_data.model_dump(),
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    updated_user = response.json()
    assert updated_user["name"] == updated_user_data.name
    assert updated_user["email_username"] == pre_existing_user.email_username
    assert updated_user["cloudname"] == pre_existing_user.cloudname


@pytest.mark.asyncio
async def test_update_user_by_id_not_found(
    test_client: AsyncClient, auth_token_admin: Token, mocker
):
    non_existent_id = uuid4()
    updated_user_data = UserPut(
        name="Updated Name",
    )

    response = await test_client.put(
        f"{settings.api_prefix}/users/{non_existent_id}",
        json=updated_user_data.model_dump(),
        headers={"Authorization": f"Bearer {auth_token_admin.access_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_user_by_id_unauthorized(test_client: AsyncClient):
    random_id = uuid4()
    updated_user_data = UserPut(
        name="Updated Name",
    )

    response = await test_client.put(
        f"{settings.api_prefix}/users/{random_id}", json=updated_user_data.model_dump()
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_update_user_by_id_insufficient_permission(
    test_client: AsyncClient,
    auth_token: Token,
    pre_existing_user: User,
    mocker,
):
    random_id = uuid4()
    updated_user_data = UserPut(
        name="Updated Name",
    )

    response = await test_client.put(
        f"{settings.api_prefix}/users/{random_id}",
        json=updated_user_data.model_dump(),
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_update_user_by_id_database_exception(
    test_client: AsyncClient,
    auth_token: Token,
    pre_existing_user: User,
    mocker,
):
    updated_user_data = UserPut(
        name="Updated Name",
    )
    mocker.patch(
        "inteliver.users.service.UserService.update_user",
        side_effect=DatabaseException("Database error"),
    )

    response = await test_client.put(
        f"{settings.api_prefix}/users/{pre_existing_user.uid}",
        json=updated_user_data.model_dump(),
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_update_user_by_id_general_exception(
    test_client: AsyncClient,
    auth_token_admin: Token,
    pre_existing_user: User,
    mocker,
):
    mocker.patch(
        "inteliver.users.service.UserService.update_user",
        side_effect=Exception("Unexpected error"),
    )
    updated_user_data = UserPut(
        name="Updated Name",
    )
    response = await test_client.put(
        f"{settings.api_prefix}/users/{pre_existing_user.uid}",
        json=updated_user_data.model_dump(),
        headers={"Authorization": f"Bearer {auth_token_admin.access_token}"},
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


# Test scenarios for patch user by id
# Endpoint patch /users/


@pytest.mark.asyncio
async def test_patch_user_by_id_success(
    test_client: AsyncClient,
    auth_token_admin: Token,
    pre_existing_user: User,
):
    patch_data = UserPatch(name="Updated Name")

    response = await test_client.patch(
        f"{settings.api_prefix}/users/{pre_existing_user.uid}",
        json=patch_data.model_dump(),
        headers={"Authorization": f"Bearer {auth_token_admin.access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    updated_user = response.json()
    assert updated_user["name"] == patch_data.name
    assert updated_user["email_username"] == pre_existing_user.email_username
    assert updated_user["cloudname"] == pre_existing_user.cloudname


@pytest.mark.asyncio
async def test_patch_user_by_id_not_found(
    test_client: AsyncClient,
    auth_token_admin: Token,
    mocker,
):
    non_existent_id = uuid4()
    patch_data = UserPatch(name="Updated Name")

    response = await test_client.patch(
        f"{settings.api_prefix}/users/{non_existent_id}",
        json=patch_data.model_dump(),
        headers={"Authorization": f"Bearer {auth_token_admin.access_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_patch_user_by_id_unauthorized(test_client: AsyncClient):
    random_id = uuid4()
    patch_data = UserPatch(name="Updated Name")

    response = await test_client.patch(
        f"{settings.api_prefix}/users/{random_id}", json=patch_data.model_dump()
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_patch_user_by_id_insufficient_permission(
    test_client: AsyncClient,
    auth_token: Token,
):
    random_id = uuid4()
    patch_data = UserPatch(name="Updated Name")

    response = await test_client.patch(
        f"{settings.api_prefix}/users/{random_id}",
        json=patch_data.model_dump(),
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_patch_user_by_id_general_exception(
    test_client: AsyncClient,
    auth_token_admin: Token,
    pre_existing_user: User,
    mocker,
):
    mocker.patch(
        "inteliver.users.service.UserService.patch_user",
        side_effect=Exception("Unexpected error"),
    )
    updated_user_data = UserPatch(
        name="Updated Name",
    )
    response = await test_client.patch(
        f"{settings.api_prefix}/users/{pre_existing_user.uid}",
        json=updated_user_data.model_dump(),
        headers={"Authorization": f"Bearer {auth_token_admin.access_token}"},
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


# Test scenarios for delete user by id
# Endpoint delete /users/


@pytest.mark.asyncio
async def test_delete_user_by_id_success(
    test_client: AsyncClient, auth_token: Token, pre_existing_user: User
):
    response = await test_client.delete(
        f"{settings.api_prefix}/users/{pre_existing_user.uid}",
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    deleted_user = response.json()
    assert deleted_user["uid"] == str(pre_existing_user.uid)
    assert deleted_user["email_username"] == pre_existing_user.email_username


@pytest.mark.asyncio
async def test_delete_user_by_id_not_found(
    test_client: AsyncClient, auth_token_admin: Token
):
    non_existent_id = uuid4()

    response = await test_client.delete(
        f"{settings.api_prefix}/users/{non_existent_id}",
        headers={"Authorization": f"Bearer {auth_token_admin.access_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_user_by_id_unauthorized(test_client: AsyncClient):
    random_id = uuid4()

    response = await test_client.delete(f"{settings.api_prefix}/users/{random_id}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_delete_user_by_id_insufficient_permission(
    test_client: AsyncClient, auth_token: Token
):
    random_id = uuid4()

    response = await test_client.delete(
        f"{settings.api_prefix}/users/{random_id}",
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_delete_user_by_id_database_exception(
    test_client: AsyncClient, auth_token: Token, pre_existing_user: User, mocker
):
    mocker.patch(
        "inteliver.users.service.UserService.delete_user",
        side_effect=DatabaseException("Database error"),
    )

    response = await test_client.delete(
        f"{settings.api_prefix}/users/{pre_existing_user.uid}",
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_delete_user_by_id_general_exception(
    test_client: AsyncClient,
    auth_token_admin: Token,
    pre_existing_user: User,
    mocker,
):
    mocker.patch(
        "inteliver.users.service.UserService.delete_user",
        side_effect=Exception("Unexpected error"),
    )

    response = await test_client.delete(
        f"{settings.api_prefix}/users/{pre_existing_user.uid}",
        headers={"Authorization": f"Bearer {auth_token_admin.access_token}"},
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
