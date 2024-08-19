from uuid import UUID

from passlib.context import CryptContext
from pydantic import EmailStr

from inteliver.auth.schemas import TokenData
from inteliver.users.schemas import UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify if the provided password matches the hashed password.

    Args:
        plain_password (str): The plain text password.
        hashed_password (str): The hashed password.

    Returns:
        bool: True if passwords match, otherwise False.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash the provided password.

    Args:
        password (str): The plain text password.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


def verify_user_id_claim(user_id: UUID, token: TokenData) -> bool:
    if token.role == UserRole.ADMIN:
        return True
    return user_id == token.sub


def verify_username_email_claim(username: EmailStr, token: TokenData) -> bool:
    if token.role == UserRole.ADMIN:
        return True
    return username == token.username
