import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from inteliver.auth.schemas import Token
from inteliver.config import settings
from inteliver.users.exceptions import DatabaseException
from inteliver.users.models import User
from inteliver.users.schemas import UserOut, UserPatch


@pytest.mark.asyncio
async def test_get_current_profile_success(
    test_client: AsyncClient, auth_token: Token, pre_existing_user: User
):
    """Test successfully retrieving a user's profile with a valid token."""
    response = await test_client.get(
        f"{settings.api_prefix}/users/profile/",
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    user_data = response.json()
    assert user_data["email_username"] == pre_existing_user.email_username
    assert user_data["name"] == pre_existing_user.name
    assert user_data["cloudname"] == pre_existing_user.cloudname


@pytest.mark.asyncio
async def test_get_current_profile_unauthorized(test_client: AsyncClient):
    response = await test_client.get(
        f"{settings.api_prefix}/users/profile/",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_current_profile_invalid_token(test_client: AsyncClient):
    response = await test_client.get(
        f"{settings.api_prefix}/users/profile/",
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_current_profile_user_not_found(
    test_client: AsyncClient,
    auth_token: Token,
    db_session: AsyncSession,
    pre_existing_user: User,
):
    # Delete the user from the database to simulate a not found scenario
    await db_session.delete(pre_existing_user)
    await db_session.commit()

    response = await test_client.get(
        f"{settings.api_prefix}/users/profile/",
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_current_profile_database_exception(
    test_client: AsyncClient, auth_token: Token, mocker
):
    mocker.patch(
        "inteliver.users.service.UserService.get_user_by_id",
        side_effect=Exception("Database error"),
    )

    response = await test_client.get(
        f"{settings.api_prefix}/users/profile/",
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_patch_current_profile_success(
    test_client: AsyncClient, auth_token: Token, pre_existing_user: User
):
    update_data = UserPatch(name="Updated Name")
    response = await test_client.patch(
        f"{settings.api_prefix}/users/profile/",
        json=update_data.model_dump(),
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    updated_user = response.json()
    assert updated_user["name"] == "Updated Name"
    assert updated_user["email_username"] == pre_existing_user.email_username
    assert updated_user["cloudname"] == pre_existing_user.cloudname


@pytest.mark.asyncio
async def test_patch_current_profile_unauthorized(test_client: AsyncClient):
    update_data = UserPatch(name="Updated Name")
    response = await test_client.patch(
        f"{settings.api_prefix}/users/profile/", json=update_data.model_dump()
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_patch_current_profile_invalid_token(test_client: AsyncClient):
    update_data = UserPatch(name="Updated Name")
    response = await test_client.patch(
        f"{settings.api_prefix}/users/profile/",
        json=update_data.model_dump(),
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_patch_current_profile_user_not_found(
    test_client: AsyncClient,
    auth_token: Token,
    db_session: AsyncSession,
    pre_existing_user: User,
):
    # Delete the user from the database to simulate a not found scenario
    await db_session.delete(pre_existing_user)
    await db_session.commit()

    update_data = UserPatch(name="Updated Name")
    response = await test_client.patch(
        f"{settings.api_prefix}/users/profile/",
        json=update_data.model_dump(),
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_patch_current_profile_database_exception(
    test_client: AsyncClient, auth_token: Token, mocker
):
    mocker.patch(
        "inteliver.users.service.UserService.patch_user",
        side_effect=DatabaseException("Database error"),
    )

    update_data = UserPatch(name="Updated Name")
    response = await test_client.patch(
        f"{settings.api_prefix}/users/profile/",
        json=update_data.model_dump(),
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_patch_current_profile_invalid_data(
    test_client: AsyncClient, auth_token: Token
):
    invalid_data = {"name": 1}
    response = await test_client.patch(
        f"{settings.api_prefix}/users/profile/",
        json=invalid_data,
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_patch_current_profile_empty_update(
    test_client: AsyncClient,
    auth_token: Token,
    pre_existing_user: User,
):
    empty_update = {}
    response = await test_client.patch(
        f"{settings.api_prefix}/users/profile/",
        json=empty_update,
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    # The user data should remain unchanged
    updated_user = response.json()
    assert UserOut(**updated_user) == UserOut.model_validate(pre_existing_user)


@pytest.mark.asyncio
async def test_patch_current_profile_email_username_change(
    test_client: AsyncClient,
    auth_token: Token,
    pre_existing_user: User,
):
    update_data = UserPatch(email_username="new_email@example.com")
    response = await test_client.patch(
        f"{settings.api_prefix}/users/profile/",
        json=update_data.model_dump(),
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    updated_user = response.json()
    # currently we do not support changing email address,
    # so the email should be same as the pre_existing user
    assert updated_user["email_username"] == pre_existing_user.email_username
