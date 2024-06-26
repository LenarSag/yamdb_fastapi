from typing import Optional
from datetime import datetime

from fastapi.exceptions import ValidationException
from pydantic import BaseModel, Field, conint, field_validator

from config import MAX_SLUG_LENGTH, MIN_SLUG_LENGTH
from models.review import Genre


class CategoryBase(BaseModel):
    name: str
    slug: str = Field(
        min_length=MIN_SLUG_LENGTH,
        max_length=MAX_SLUG_LENGTH,
        pattern=r"^[-a-zA-Z0-9_]+$",
    )

    class Config:
        from_attributes = True


class GenreBase(BaseModel):
    name: str
    slug: str = Field(
        min_length=MIN_SLUG_LENGTH,
        max_length=MAX_SLUG_LENGTH,
        pattern=r"^[-a-zA-Z0-9_]+$",
    )

    class Config:
        from_attributes = True


class TitleCreate(BaseModel):
    name: str
    year: int
    description: Optional[str]
    genre: list[str]
    category: str

    @field_validator("year")
    @classmethod
    def validate_year(cls, year):
        if year > datetime.now().year:
            raise ValidationException("Year cant be more than current year")
        return year

    class Config:
        from_attributes = True


class TitleOut(BaseModel):
    name: str
    year: int
    rating: Optional[float]
    description: Optional[str]
    genres: list[GenreBase]
    category: CategoryBase


class ReviewCreate(BaseModel):
    text: str
    score: conint(ge=1, le=10)

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class ReviewOut(ReviewCreate):
    id: int
    author: str
    pub_date: datetime


class CommentCreate(BaseModel):
    text: str

    class Config:
        from_attributes = True


class CommentOut(CommentCreate):
    id: int
    author: str
    pub_date: datetime
