import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID

from inteliver.database.postgres import Base
from inteliver.users.schemas import UserRole


class User(Base):
    __tablename__ = "users"

    uid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String, nullable=False)
    cloudname = Column(String, unique=True, nullable=False)
    email_username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False, default=str(UserRole.USER.value))
    email_activated = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now().replace(tzinfo=None))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now().replace(tzinfo=None),
        onupdate=lambda: datetime.now().replace(tzinfo=None),
    )
