from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from inteliver.auth.exceptions import NotEnoughPermissionException
from inteliver.auth.schemas import TokenData
from inteliver.auth.service import AuthService
from inteliver.auth.utils import verify_user_id_claim, verify_username_email_claim
from inteliver.database.dependencies import get_db
from inteliver.users.exceptions import (
    DatabaseException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from inteliver.users.schemas import UserCreate, UserOut, UserPut, UserRole, UserUpdate
from inteliver.users.service import UserService

router = APIRouter()


@router.post(
    "/", response_model=UserOut, status_code=status.HTTP_201_CREATED, tags=["Users"]
)
async def create_new_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(AuthService.has_role(UserRole.ADMIN)),
):
    """
    API endpoint route creating a new user.

    Args:
        user (UserCreate): The user data transfer object with creation details.
        db (AsyncSession): The database session dependency.

    Returns:
        UserOut: The created user data transfer object.

    Raises:
        UserAlreadyExistsException: If the user already exists.
        HTTPException: If any other error occurs.
    """
    try:
        return await UserService.create_user(db, user)
    except UserAlreadyExistsException:
        raise
    except DatabaseException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/{user_id}", response_model=UserOut, tags=["Users"])
async def get_user_by_id(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(AuthService.has_role(UserRole.USER)),
):
    """
    API endpoint route for getting a user info by user_id .

    Args:
        user_id (UUID): The user id.
        db (AsyncSession): The database session dependency.

    Returns:
        UserOut: The retrieved user data transfer object.

    Raises:
        UserNotFoundException: If the user with user_id not found.
        DatabaseException: If a database error occurs.
        HTTPException: If any other error occurs.
    """
    if not verify_user_id_claim(user_id=user_id, token=current_user):
        raise NotEnoughPermissionException
    try:
        return await UserService.get_user_by_id(db, user_id)
    except UserNotFoundException:
        raise
    except DatabaseException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/by-email/", response_model=UserOut, tags=["Users"])
async def get_user_by_email(
    email: EmailStr,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(AuthService.has_role(UserRole.USER)),
):
    """Get a user by email via a GET request.

    Args:
        email (EmailStr): The email of the user to retrieve.
        db (AsyncSession): The database session dependency.

    Returns:
        UserOut: The user data transfer object.

    Raises:
        UserNotFoundException: If the user with user_id not found.
        DatabaseException: If a database error occurs.
        HTTPException: If any other error occurs.
    """
    if not verify_username_email_claim(username=email, token=current_user):
        raise NotEnoughPermissionException
    try:
        return await UserService.get_user_by_email(db, email)
    except UserNotFoundException as e:
        raise e
    except DatabaseException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/", response_model=list[UserOut], tags=["Users"])
async def get_all_users(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(AuthService.has_role(UserRole.ADMIN)),
):
    """
    Retrieve all users through the API endpoint with pagination.

    Args:
        skip (int): The number of records to skip.
        limit (int): The maximum number of records to return.
        db (AsyncSession): The database session dependency.

    Returns:
        list[UserOut]: A list of user data transfer objects.

    Raises:
        DatabaseException: If a database error occurs.
        HTTPException: If any other error occurs.
    """
    try:
        return await UserService.get_all_users(db, skip, limit)

    except DatabaseException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/{user_id}", response_model=UserOut, tags=["Users"])
async def update_user_by_id(
    user_id: UUID,
    user_put: UserPut,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(AuthService.has_role(UserRole.USER)),
):
    """
    Update a user by ID via a PUT request.

    Args:
        user_id (UUID): The ID of the user to update.
        user_put (UserPut): The complete updated user information.
        db (AsyncSession): The database session dependency.

    Returns:
        UserOut: The updated user data transfer object.

    Raises:
        UserNotFoundException: If the user with user_id not found.
        DatabaseException: If a database error occurs.
        HTTPException: If the user is not found or any other error occurs.
    """
    if not verify_user_id_claim(user_id=user_id, token=current_user):
        raise NotEnoughPermissionException
    try:
        return await UserService.update_user(db, user_id, user_put)
    except UserNotFoundException:
        raise
    except DatabaseException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.patch("/{user_id}", response_model=UserOut, tags=["Users"])
async def patch_user_by_id(
    user_id: UUID,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(AuthService.has_role(UserRole.USER)),
):
    """
    Patch a user by ID via a PATCH request.

    Args:
        user_id (UUID): The ID of the user to update.
        user_update (UserUpdate): The partial updated user information.
        db (AsyncSession): The database session dependency.

    Returns:
        UserOut: The updated user data transfer object.

    Raises:
        UserNotFoundException: If the user does not exist.
        DatabaseException: If a database error occurs.
        HTTPException: If any other error occurs.
    """
    if not verify_user_id_claim(user_id=user_id, token=current_user):
        raise NotEnoughPermissionException
    try:
        return await UserService.patch_user(db, user_id, user_update)
    except UserNotFoundException:
        raise
    except DatabaseException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/{user_id}", response_model=UserOut, tags=["Users"])
async def delete_user_by_id(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(AuthService.has_role(UserRole.USER)),
):
    """Delete a user by ID via a DELETE request.

    Args:
        user_id (UUID): The ID of the user to delete.
        db (AsyncSession): The database session dependency.

    Returns:
        UserOut: The deleted user data transfer object.

    Raises:
        UserNotFoundException: If the user does not exist.
        DatabaseException: If a database error occurs.
        HTTPException: If any other error occurs.
    """
    if not verify_user_id_claim(user_id=user_id, token=current_user):
        raise NotEnoughPermissionException
    try:
        return await UserService.delete_user(db, user_id)
    except UserNotFoundException:
        raise
    except DatabaseException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/profile/", response_model=UserOut, tags=["Profile"])
async def get_current_profile(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(AuthService.has_role(UserRole.USER)),
):
    """
    API endpoint route for getting a user profile based on the bearer token sub.

    Args:
        db (AsyncSession): The database session dependency.

    Returns:
        UserOut: The retrieved user data transfer object.

    Raises:
        UserNotFoundException: If the user with user_id not found.
        DatabaseException: If a database error occurs.
        HTTPException: If any other error occurs.
    """
    # TODO: forward the request to GET /user/{user_id} with current_user.sub

    try:
        return await UserService.get_user_by_id(db, current_user.sub)
    except UserNotFoundException:
        raise
    except DatabaseException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.patch("/profile/", response_model=UserOut, tags=["Profile"])
async def patch_current_profile(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(AuthService.has_role(UserRole.USER)),
):
    """
    Patch current user profile by ID based on the bearer token sub.

    Args:
        user_update (UserUpdate): The partial updated user information.
        db (AsyncSession): The database session dependency.

    Returns:
        UserOut: The updated user data transfer object.

    Raises:
        UserNotFoundException: If the user does not exist.
        DatabaseException: If a database error occurs.
        HTTPException: If any other error occurs.
    """
    # TODO: forward the request to PATCH /user/{user_id} with current_user.sub

    try:
        return await UserService.patch_user(db, current_user.sub, user_update)
    except UserNotFoundException:
        raise
    except DatabaseException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/profile/", response_model=UserOut, tags=["Profile"])
async def delete_current_profile(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(AuthService.has_role(UserRole.USER)),
):
    """Delete a user by ID based on the bearer token sub.

    Args:
        db (AsyncSession): The database session dependency.

    Returns:
        UserOut: The deleted user data transfer object.

    Raises:
        UserNotFoundException: If the user does not exist.
        DatabaseException: If a database error occurs.
        HTTPException: If any other error occurs.
    """
    # TODO: forward the request to DELETE /user/{user_id} with current_user.sub

    try:
        return await UserService.delete_user(db, current_user.sub)
    except UserNotFoundException:
        raise
    except DatabaseException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
