from typing import Optional
from uuid import UUID

from loguru import logger
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from inteliver.users.exceptions import (
    DatabaseException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from inteliver.users.models import User
from inteliver.users.schemas import UserPut, UserUpdate


class UserCRUD:
    @staticmethod
    async def create_user(db: AsyncSession, db_user: User) -> User:
        """
        Create a new user in the database.

        Args:
            db (AsyncSession): The database session.
            user (User): The user model instance to be added to the database.

        Returns:
            User: The created user model instance.

        Raises:
            UserAlreadyExistsException: If the user already exists in the database.
            DatabaseException: If a general database error occurs.
        """
        try:
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
            return db_user

        except IntegrityError:
            await db.rollback()
            raise UserAlreadyExistsException(
                detail=f"User with this email ({db_user.email_username}) already exists."
            )

        except SQLAlchemyError as e:
            await db.rollback()
            raise DatabaseException(detail=str(e))

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
        """
        Retrieve a user by user_id from the database.

        Args:
            db (AsyncSession): The database session.
            user_id (UUID): The user id.

        Returns:
            User: The user database model with the matching user_id.

        Raises:
            DatabaseException: If a general database error occurs.
        """
        try:
            return await db.get(User, user_id)
        except SQLAlchemyError as e:
            await db.rollback()
            raise DatabaseException(detail=str(e))

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get a user by email from the database.

        Args:
            db (AsyncSession): The database session.
            email (str): The email of the user to retrieve.

        Returns:
            User: The user database model.

        Raises:
            UserNotFoundException: If the user does not exist.
            DatabaseException: If a database error occurs.
        """
        try:
            result = await db.execute(select(User).filter_by(email_username=email))
            return result.scalar_one_or_none()

        except SQLAlchemyError as e:
            raise DatabaseException(detail=str(e))

    @staticmethod
    async def get_user_by_cloudname(db: AsyncSession, cloudname: str) -> Optional[User]:
        """Get a user by cloudname from the database.

        Args:
            db (AsyncSession): The database session.
            cloudname (str): The cloudname of the user to retrieve.

        Returns:
            User: The user database model.

        Raises:
            UserNotFoundException: If the user does not exist.
            DatabaseException: If a database error occurs.
        """
        try:
            result = await db.execute(select(User).filter_by(cloudname=cloudname))
            return result.scalar_one_or_none()

        except SQLAlchemyError as e:
            raise DatabaseException(detail=str(e))

    @staticmethod
    async def get_all_users(
        db: AsyncSession, skip: int = 0, limit: int = 10
    ) -> list[User]:
        """
        Retrieve all users from the database with pagination.

        Args:
            db (AsyncSession): The database session.
            skip (int): The number of records to skip.
            limit (int): The maximum number of records to return.

        Returns:
            list[User]: A list of user database models.

        Raises:
            DatabaseException: If a database error occurs.
        """
        try:
            result = await db.execute(select(User).offset(skip).limit(limit))
            users = result.scalars().all()
            return list(users)
        except SQLAlchemyError as e:
            await db.rollback()
            raise DatabaseException(detail=str(e))

    @staticmethod
    async def update_user(db: AsyncSession, user_id: UUID, user_put: UserPut) -> User:
        """
        Update a user in the database with new information.

        Args:
            db (AsyncSession): The database session.
            user_id (UUID): The ID of the user to update.
            user_put (UserPut): The updated user information.

        Returns:
            User: The updated user database model.

        Raises:
            UserNotFoundException: If the user does not exist.
            DatabaseException: If a database error occurs.
        """
        try:
            db_user = await UserCRUD.get_user_by_id(db, user_id)

            if db_user is None:
                raise UserNotFoundException(f"User with id ({user_id}) not found")

            for field, value in user_put.model_dump(exclude_unset=True).items():
                setattr(db_user, field, value)

            await db.commit()
            await db.refresh(db_user)
            return db_user

        except SQLAlchemyError as e:
            await db.rollback()
            raise DatabaseException(detail=str(e))

    @staticmethod
    async def patch_user(
        db: AsyncSession, user_id: UUID, user_update: UserUpdate
    ) -> User:
        """
        Patch a user in the database with new information.

        Args:
            db (AsyncSession): The database session.
            user_id (UUID): The ID of the user to update.
            user_update (UserUpdate): The partial updated user information.

        Returns:
            User: The updated user database model.

        Raises:
            UserNotFoundException: If the user does not exist.
            DatabaseException: If a database error occurs.
        """
        try:
            db_user = await UserCRUD.get_user_by_id(db, user_id)

            if db_user is None:
                raise UserNotFoundException(f"User with id ({user_id}) not found")

            for field, value in user_update.model_dump(exclude_unset=True).items():
                setattr(db_user, field, value)

            await db.commit()
            await db.refresh(db_user)
            return db_user
        except SQLAlchemyError as e:
            raise DatabaseException(detail=str(e))

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: UUID) -> User:
        """Delete a user by ID from the database.

        Args:
            db (AsyncSession): The database session.
            user_id (UUID): The ID of the user to delete.

        Returns:
            User: The deleted user database model.

        Raises:
            UserNotFoundException: If the user does not exist.
            DatabaseException: If a database error occurs.
        """
        try:
            db_user = await UserCRUD.get_user_by_id(db, user_id)

            if db_user is None:
                raise UserNotFoundException(f"User with id {user_id} not found")
            # TODO: deleting cloudname storage space and data
            await db.delete(db_user)
            await db.commit()
            return db_user
        except SQLAlchemyError as e:
            raise DatabaseException(detail=str(e))

    @staticmethod
    async def update_user_password(
        db: AsyncSession, db_user: User, new_password_hashed: str
    ) -> None:
        """
        Update the password of a user.

        Args:
            db (AsyncSession): The database session.
            db_user (User): The user object db model.
            new_password_hashed (str): The new hashed password.

        Returns:
            User: The updated user database model.
        """
        db_user.password = new_password_hashed
        await db.commit()
        await db.refresh(db_user)

    @staticmethod
    async def validate_user_email(db: AsyncSession, user: User):
        """
        Validate the user's email.

        Args:
            db (AsyncSession): The database session.
            user (User): The user object.
        """
        logger.debug("user is now activated.")
        user.email_activated = True
        await db.commit()
        await db.refresh(user)

    @staticmethod
    async def get_cloudname(db: AsyncSession, user_id: UUID) -> str:
        """Get the cloudname of a user by their user ID from the database.

        Args:
            db (AsyncSession): The database session.
            user_id (UUID): The unique identifier of the user to retrieve.

        Returns:
            str: The cloudname of the user.

        Raises:
            UserNotFoundException: If the user does not exist.
            DatabaseException: If a database error occurs.
        """
        try:
            result = await db.execute(select(User.cloudname).filter_by(uid=user_id))
            return result.scalar_one_or_none()

        except SQLAlchemyError as e:
            raise DatabaseException(detail=str(e))
