import pytest
from fastapi import status
from httpx import AsyncClient

from inteliver.auth.exceptions import DatabaseException
from inteliver.auth.schemas import PasswordChange, Token
from inteliver.config import settings
from inteliver.users.models import User
from inteliver.users.schemas import UserCreate

# Test scenarios for user login
# Endpoint post /auth/login


@pytest.mark.asyncio
async def test_login_success(test_client: AsyncClient, pre_existing_user: User):
    response = await test_client.post(
        f"{settings.api_prefix}/auth/login",
        data={"username": pre_existing_user.email_username, "password": "password123"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_failure(test_client: AsyncClient):
    response = await test_client.post(
        f"{settings.api_prefix}/auth/login",
        data={"username": "nonexistent@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Test scenarios for getting refresh token
# Endpoint post /auth/refresh


@pytest.mark.asyncio
async def test_refresh_token_success(test_client: AsyncClient, auth_token: Token):
    response = await test_client.post(
        f"{settings.api_prefix}/auth/refresh",
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_token_invalid_token(test_client: AsyncClient):
    response = await test_client.post(
        f"{settings.api_prefix}/auth/refresh",
        headers={"Authorization": "Bearer invalidtoken"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Test scenarios for logout
# Endpoint post /auth/logout


@pytest.mark.asyncio
async def test_logout_success(test_client: AsyncClient, auth_token: Token):
    response = await test_client.post(
        f"{settings.api_prefix}/auth/logout",
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["msg"].startswith("Successfully logged out")


@pytest.mark.asyncio
async def test_logout_invalid_token(test_client: AsyncClient):
    response = await test_client.post(
        f"{settings.api_prefix}/auth/logout",
        headers={"Authorization": "Bearer invalidtoken"},
    )
    print(response.json())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Test scenarios for user changing password
# Endpoint post /auth/change-password


@pytest.mark.asyncio
async def test_change_password_success(test_client: AsyncClient, auth_token: Token):
    password_change = PasswordChange(
        current_password="password123", new_password="newpassword123"
    )
    response = await test_client.post(
        f"{settings.api_prefix}/auth/change-password",
        json=password_change.model_dump(),
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["msg"] == "Password changed successfully"


@pytest.mark.asyncio
async def test_change_password_incorrect_current_password(
    test_client: AsyncClient, auth_token: Token
):
    password_change = PasswordChange(
        current_password="wrongpassword", new_password="newpassword123"
    )
    response = await test_client.post(
        f"{settings.api_prefix}/auth/change-password",
        json=password_change.model_dump(),
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_register_user_success(
    test_client: AsyncClient, user_create_data: UserCreate
):

    response = await test_client.post(
        f"{settings.api_prefix}/auth/register", json=user_create_data.model_dump()
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email_username"] == user_create_data.email_username
    assert "uid" in data


@pytest.mark.asyncio
async def test_register_user_already_exists(
    test_client: AsyncClient,
    user_create_data: UserCreate,
):
    response = await test_client.post(
        f"{settings.api_prefix}/auth/register", json=user_create_data.model_dump()
    )
    response = await test_client.post(
        f"{settings.api_prefix}/auth/register", json=user_create_data.model_dump()
    )
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_register_user_database_error(
    test_client: AsyncClient,
    user_create_data: UserCreate,
    mocker,
):
    mocker.patch(
        "inteliver.auth.service.AuthService.register_user",
        side_effect=DatabaseException("Database error"),
    )
    response = await test_client.post(
        f"{settings.api_prefix}/auth/register", json=user_create_data.model_dump()
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
