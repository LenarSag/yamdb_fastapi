from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

from models.user import UserRoles
from config import MAX_USERNAME_LENGTH, MAX_EMAIL_LENGTH


class UserCreate(BaseModel):
    username: str = Field(max_length=MAX_USERNAME_LENGTH, pattern=r"^[\w.@+-]+$")
    email: EmailStr = Field(max_length=MAX_EMAIL_LENGTH)


class UserGetToken(BaseModel):
    username: str = Field(max_length=150, pattern=r"^[\w.@+-]+$")
    confirmation_code: UUID


class UserForUser(UserCreate):
    id: int
    firt_name: Optional[str] = Field(max_length=MAX_USERNAME_LENGTH)
    last_name: Optional[str] = Field(max_length=MAX_USERNAME_LENGTH)
    bio: Optional[str]


class UserForAdmin(UserForUser):
    role: UserRoles = Field(default=UserRoles.USER)
