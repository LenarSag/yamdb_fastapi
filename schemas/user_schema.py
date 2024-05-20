from typing import Optional

from fastapi.exceptions import ValidationException
from pydantic import BaseModel, EmailStr, Field, field_validator

from models.user import UserRoles
from config import MAX_USERNAME_LENGTH, MAX_EMAIL_LENGTH


class UserAuth(BaseModel):
    id: int
    username: str


class UserCreate(BaseModel):
    username: str = Field(max_length=MAX_USERNAME_LENGTH, pattern=r"^[\w.@+-]+$")
    email: EmailStr = Field(max_length=MAX_EMAIL_LENGTH)

    @field_validator("username")
    @classmethod
    def validate_username(cls, username):
        if username and username.lower() == "me":
            raise ValidationException("Username can't be <me>")
        return username

    class Config:
        from_attributes = True


class UserGetToken(BaseModel):
    username: str = Field(max_length=150, pattern=r"^[\w.@+-]+$")
    confirmation_code: str

    class Config:
        from_attributes = True


class UserForUser(UserCreate):
    id: int
    firt_name: Optional[str] = Field(max_length=MAX_USERNAME_LENGTH)
    last_name: Optional[str] = Field(max_length=MAX_USERNAME_LENGTH)
    bio: Optional[str]


class UserForAdmin(UserForUser):
    role: UserRoles = Field(default=UserRoles.USER)
