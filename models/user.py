import re
import uuid
from typing import Optional
from enum import Enum as PyEnum

from sqlalchemy import (
    String,
    Enum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import validates

from models.base import Base
from config import MAX_USERNAME_LENGTH, MAX_EMAIL_LENGTH


def generate_uuid_str():
    return str(uuid.uuid4())


class UserRoles(PyEnum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String(MAX_USERNAME_LENGTH), unique=True, nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(
        String(MAX_EMAIL_LENGTH), unique=True, nullable=False
    )
    first_name: Mapped[Optional[str]]
    last_name: Mapped[Optional[str]]
    is_superuser: Mapped[bool] = mapped_column(default=False)
    bio: Mapped[Optional[str]]
    role: Mapped[UserRoles] = mapped_column(
        Enum(UserRoles, values_callable=lambda obj: [e.value for e in obj]),
        default=UserRoles.USER.value,
        server_default=UserRoles.USER.value,
    )
    confirmation_code: Mapped[str] = mapped_column(default=generate_uuid_str)

    reviews = relationship(
        "Review", back_populates="author", cascade="all, delete-orphan"
    )
    comments = relationship(
        "Comment", back_populates="author", cascade="all, delete-orphan"
    )

    @validates("username")
    def validate_username(self, key, value):
        username_regex = r"^[\w.@+-]+$"
        if not re.match(username_regex, value):
            raise ValueError("Username is invalid")
        if value and value.lower() == "me":
            raise ValueError("Username cant be me")
        return value

    @validates("email")
    def validate_email(self, key, value):
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, value):
            raise ValueError("Invalid email format")
        return value

    def __str__(self) -> str:
        return self.username

    @property
    def is_admin(self):
        return self.role == UserRoles.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == UserRoles.MODERATOR
