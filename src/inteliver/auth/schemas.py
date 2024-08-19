from uuid import UUID

from pydantic import BaseModel, EmailStr

from inteliver.users.schemas import UserRole


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    sub: UUID
    role: UserRole
    username: str


class LoginForm(BaseModel):
    username: str
    password: str


class OTPForm(BaseModel):
    username: str
    otp: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class TokenSub(BaseModel):
    sub: UUID
