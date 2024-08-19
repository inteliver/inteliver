from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class UserCreate(BaseModel):
    name: str
    email_username: EmailStr
    cloudname: str
    password: str


class UserUpdate(BaseModel):
    name: str | None = None


class UserPut(BaseModel):
    name: str


class UserOut(BaseModel):
    uid: UUID
    name: str
    email_username: str
    cloudname: str
    role: UserRole
    email_activated: bool
    created_at: datetime | None
    updated_at: datetime | None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email_username: EmailStr
    password: str


class EmailValidation(BaseModel):
    email_username: EmailStr
    validation_token: str


class EmailResendRequest(BaseModel):
    email_username: EmailStr
