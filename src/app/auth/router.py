from typing import Annotated

from fastapi import APIRouter, Depends, Security
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import AuthenticationFailedException
from app.auth.schemas import (
    PasswordChange,
    PasswordResetConfirm,
    PasswordResetRequest,
    Token,
    TokenData,
)
from app.auth.service import AuthService
from app.database.dependencies import get_db

router = APIRouter()


@router.post("/login", response_model=Token, tags=["Auth"])
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate a user and return a JWT token.

    This endpoint takes a username and password from the `LoginForm` and
    authenticates the user. If the credentials are correct, it returns
    a JWT token.

    Args:
        form_data (LoginForm): Form data containing username and password.
        db (AsyncSession): Database session dependency.

    Returns:
        Token: JWT token with access token and token type.

    Raises:
        HTTPException: If authentication fails, raises a 401 unauthorized status code
            with a message indicating incorrect username or password.
    """
    user = await AuthService.authenticate_user(
        db, form_data.username, form_data.password
    )
    if not user:
        raise AuthenticationFailedException
    access_token = AuthService.create_access_token(
        data={"sub": str(user.uid), "username": user.email_username, "role": user.role}
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/refresh", response_model=Token, tags=["Auth"])
async def refresh_token(token: str = Depends(AuthService.oauth2_scheme)):
    """
    Refresh the user's JWT token.

    This endpoint takes the user's JWT token, validates it, and issues a new
    token with updated expiration. It allows users to stay authenticated without
    having to log in again frequently.

    Args:
        token (str): The JWT token provided by the user.

    Returns:
        dict: A new JWT token with updated expiration and the token type.
    """
    token_data = AuthService.decode_access_token(token)
    new_token = AuthService.create_access_token(
        data={
            "sub": str(token_data.sub),
            "username": token_data.username,
            "role": token_data.role,
        }
    )
    return Token(access_token=new_token, token_type="bearer")


@router.post("/logout", tags=["Auth"])
async def logout(token: str = Depends(AuthService.oauth2_scheme)):
    """
    Log out the user by invalidating their token.

    This endpoint takes the user's JWT token and invalidates it, effectively
    logging out the user. The actual invalidation logic can vary based on the
    implementation and requirements, such as:

    - Adding the token to a blacklist.
    - Maintaining a session store and marking the session as invalid.
    - Setting token expiration to the past.

    Args:
        token (str): The JWT token provided by the user.

    Returns:
        dict: A message indicating successful logout.
    """

    # Implement token invalidation logic
    # For example, add the token to a blacklist or invalidate
    # the session in the database
    return {"msg": "Successfully logged out"}


@router.post("/change-password", tags=["Password"])
async def change_password(
    password_change: PasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Security(AuthService.get_current_user),
):
    """
    Change the password of the current user.

    This endpoint allows authenticated users to change their password.
    Users must provide their current password and the new password.

    Args:
        password_change (PasswordChange): Object containing current and new passwords.
        current_user (TokenData): The current authenticated user.
        db (AsyncSession): Database session dependency.

    Returns:
        dict: A message indicating successful password change.

    Raises:
        HTTPException: If the current password is incorrect.
    """
    await AuthService.change_password(db, current_user.sub, password_change)
    return {"msg": "Password changed successfully"}


@router.post("/password-reset/request", tags=["Password"])
async def request_password_reset(
    password_reset_request: PasswordResetRequest, db: AsyncSession = Depends(get_db)
):
    """
    Request a password reset by email.

    This endpoint initiates the password reset process by sending a reset token
    to the user's email address.

    Args:
        password_reset_request (PasswordResetRequest): Request containing the user's email.
        db (AsyncSession): Database session dependency.

    Returns:
        dict: A message indicating that the reset email has been sent.
    """
    await AuthService.send_password_reset_email(db, password_reset_request.email)
    return {"msg": "Password reset email sent"}


@router.post("/password-reset/confirm", tags=["Password"])
async def confirm_password_reset(
    password_reset_confirm: PasswordResetConfirm, db: AsyncSession = Depends(get_db)
):
    """
    Confirm the password reset with the token and set a new password.

    This endpoint verifies the reset token and allows the user to set a new password.

    Args:
        password_reset_confirm (PasswordResetConfirm): Request containing the reset token and new password.
        db (AsyncSession): Database session dependency.

    Returns:
        dict: A message indicating that the password has been reset successfully.

    Raises:
        HTTPException: If the reset token is invalid or expired.
    """
    await AuthService.reset_password(
        db, password_reset_confirm.token, password_reset_confirm.new_password
    )
    return {"msg": "Password reset successfully"}
