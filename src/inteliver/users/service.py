from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from inteliver.auth.utils import get_password_hash
from inteliver.storage.exceptions import CludnameNotSetException
from inteliver.users.crud import UserCRUD
from inteliver.users.exceptions import UserNotFoundException
from inteliver.users.models import User
from inteliver.users.schemas import UserCreate, UserOut, UserPut, UserUpdate


class UserService:
    @staticmethod
    async def create_user(db: AsyncSession, user: UserCreate) -> UserOut:
        """
        Service to create a new user.

        Args:
            db (AsyncSession): The database session.
            user (UserCreate): The user data transfer object with creation details.

        Returns:
            User: The created user model instance.

        Raises:
            UserAlreadyExistsException: If the user already exists in the database.
            DatabaseException: If a general database error occurs.
            ValidationError: If the database model could not be validated.
        """
        db_user = User(**user.model_dump())
        db_user.password = get_password_hash(user.password)
        db_user = await UserCRUD.create_user(db, db_user)
        return UserOut.model_validate(db_user)

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: UUID) -> UserOut:
        """
        Service to retrieve a user by user id.

        Args:
            db (AsyncSession): The database session.
            user_id (UUID): The user id.

        Returns:
            User: The user info with the user_id.

        Raises:
            UserNotFoundException: If the user with user_id does not exist in database.
            DatabaseException: If a general database error occurs.
            ValidationError: If the database model could not be validated.
        """
        db_user = await UserCRUD.get_user_by_id(db, user_id)

        if db_user is None:
            raise UserNotFoundException(f"User with id ({user_id}) not found")

        return UserOut.model_validate(db_user)

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> UserOut:
        """Get a user by email via the service layer.

        Args:
            db (AsyncSession): The database session.
            email (str): The email of the user to retrieve.

        Returns:
            User: The user database model.

        Raises:
            UserNotFoundException: If the user does not exist.
            DatabaseException: If a database error occurs.
            ValidationError: If the database model could not be validated.
        """
        db_user = await UserCRUD.get_user_by_email(db, email)

        if db_user is None:
            raise UserNotFoundException(f"User with email {email} not found")

        return UserOut.model_validate(db_user)

    @staticmethod
    async def get_user_by_cloudname(db: AsyncSession, cloudname: str) -> UserOut:
        """Get a user by cloudname via the service layer.

        Args:
            db (AsyncSession): The database session.
            cloudname (str): The cloudname of the user to retrieve.

        Returns:
            User: The user database model.

        Raises:
            UserNotFoundException: If the user does not exist.
            DatabaseException: If a database error occurs.
            ValidationError: If the database model could not be validated.
        """
        db_user = await UserCRUD.get_user_by_cloudname(db, cloudname)

        if db_user is None:
            raise UserNotFoundException(f"User with cloudname {cloudname} not found")

        return UserOut.model_validate(db_user)

    @staticmethod
    async def get_all_users(
        db: AsyncSession, skip: int = 0, limit: int = 10
    ) -> list[UserOut]:
        """
        Retrieve all users from the database with pagination via the service layer.

        Args:
            db (AsyncSession): The database session.
            skip (int): The number of records to skip.
            limit (int): The maximum number of records to return.

        Returns:
            list[UserOut]: A list of user schemas.

        Raises:
            DatabaseException: If a database error occurs.
            ValidationError: If the database model could not be validated.
        """
        users = await UserCRUD.get_all_users(db, skip, limit)
        return [UserOut.model_validate(user) for user in users]

    @staticmethod
    async def update_user(
        db: AsyncSession, user_id: UUID, user_put: UserPut
    ) -> UserOut:
        """
        Update a user via the service layer.

        Args:
            db (AsyncSession): The database session.
            user_id (UUID): The ID of the user to update.
            user_put (UserPut): The completed updated user information.

        Returns:
            UserOut: The updated user schema.

        Raises:
            UserNotFoundException: If the user does not exist.
            DatabaseException: If a database error occurs.
        """

        db_user = await UserCRUD.update_user(db, user_id, user_put)
        return UserOut.model_validate(db_user)

    @staticmethod
    async def patch_user(
        db: AsyncSession, user_id: UUID, user_update: UserUpdate
    ) -> UserOut:
        """
        Patch a user via the service layer.

        Args:
            db (AsyncSession): The database session.
            user_id (UUID): The ID of the user to update.
            user_update (UserUpdate): The partial updated user information.

        Returns:
            UserOut: The updated user schema.

        Raises:
            UserNotFoundException: If the user does not exist.
            DatabaseException: If a database error occurs.
        """
        db_user = await UserCRUD.patch_user(db, user_id, user_update)
        return UserOut.model_validate(db_user)

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: UUID) -> UserOut:
        """Delete a user via the service layer.

        Args:
            db (AsyncSession): The database session.
            user_id (UUID): The ID of the user to delete.

        Returns:
            UserOut: The deleted user schema.

        Raises:
            UserNotFoundException: If the user does not exist.
            DatabaseException: If a database error occurs.
        """
        deleted_user = await UserCRUD.delete_user(db, user_id)
        return UserOut.model_validate(deleted_user)

    @staticmethod
    async def get_cloudname(db: AsyncSession, user_id: UUID) -> str:
        cloudname = await UserCRUD.get_cloudname(db, user_id)
        if not cloudname:
            raise CludnameNotSetException
        return cloudname
