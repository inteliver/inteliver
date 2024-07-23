from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dependencies import get_db
from app.users.exceptions import (
    DatabaseException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.users.schemas import UserCreate, UserOut, UserPut, UserUpdate
from app.users.service import UserService

router = APIRouter()


@router.post("/", response_model=UserOut)
async def create_new_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
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
    except UserAlreadyExistsException as e:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/{user_id}", response_model=UserOut)
async def get_user_by_id(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
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
    try:
        return await UserService.get_user_by_id(db, user_id)
    except UserNotFoundException as e:
        raise
    except DatabaseException as e:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/by-email/", response_model=UserOut)
async def get_user_by_email(email: EmailStr, db: AsyncSession = Depends(get_db)):
    """Get a user by email via a GET request.

    Args:
        email (EmailStr): The email of the user to retrieve.
        db (AsyncSession): The database session dependency.

    Returns:
        UserOut: The user data transfer object.

    Raises:
        UserNotFoundException: If the user with user_id not found.
        DatabaseException: If a database error occurs.
        HTTPException: If any other error occurs."""
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


@router.get("/", response_model=list[UserOut])
async def get_all_users(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
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

    except DatabaseException as e:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/{user_id}", response_model=UserOut)
async def update_user_by_id(
    user_id: UUID, user_put: UserPut, db: AsyncSession = Depends(get_db)
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
    try:
        return await UserService.update_user(db, user_id, user_put)
    except UserNotFoundException as e:
        raise
    except DatabaseException as e:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.patch("/{user_id}", response_model=UserOut)
async def patch_user_by_id(
    user_id: UUID, user_update: UserUpdate, db: AsyncSession = Depends(get_db)
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
    try:
        return await UserService.patch_user(db, user_id, user_update)
    except UserNotFoundException as e:
        raise
    except DatabaseException as e:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/{user_id}", response_model=UserOut)
async def delete_user_by_id(user_id: UUID, db: AsyncSession = Depends(get_db)):
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
    try:
        deleted_user = await UserService.delete_user(db, user_id)
        return UserOut.model_validate(deleted_user)
    except UserNotFoundException as e:
        raise e
    except DatabaseException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
