from uuid import UUID

import bcrypt
from pydantic import EmailStr

from inteliver.auth.schemas import TokenData
from inteliver.users.schemas import UserRole


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify if the provided password matches the hashed password.

    Args:
        plain_password (str): The plain text password.
        hashed_password (str): The hashed password.

    Returns:
        bool: True if passwords match, otherwise False.
    """
    password_byte_enc = plain_password.encode("utf-8")
    hashed_password_byte_enc = hashed_password.encode("utf-8")
    return bcrypt.checkpw(
        password=password_byte_enc, hashed_password=hashed_password_byte_enc
    )


def get_password_hash(password: str) -> str:
    """
    Hash the provided password.

    Args:
        password (str): The plain text password.

    Returns:
        str: The hashed password.
    """
    pwd_bytes = password.encode("utf-8")
    return bcrypt.hashpw(password=pwd_bytes, salt=bcrypt.gensalt()).decode("utf-8")


def verify_user_id_claim(user_id: UUID, token: TokenData) -> bool:
    if token.role == UserRole.ADMIN:
        return True
    return user_id == token.sub


def verify_username_email_claim(username: EmailStr, token: TokenData) -> bool:
    if token.role == UserRole.ADMIN:
        return True
    return username == token.username
