from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field, conint, field_validator, ValidationError

from config import MAX_SLUG_LENGTH, MIN_SLUG_LENGTH


class CategoryCreate(BaseModel):
    name: str
    slug: str = Field(
        min_length=MIN_SLUG_LENGTH,
        max_length=MAX_SLUG_LENGTH,
        pattern=r"^[-a-zA-Z0-9_]+$",
    )


class CategoryDB(CategoryCreate):
    id: int


class GenreCreate(BaseModel):
    name: str
    slug: str = Field(
        min_length=MIN_SLUG_LENGTH,
        max_length=MAX_SLUG_LENGTH,
        pattern=r"^[-a-zA-Z0-9_]+$",
    )


class GenreDB(GenreCreate):
    id: int


class TitleCreate(BaseModel):
    name: str
    year: int
    genre: str
    category: str

    @field_validator("year")
    @classmethod
    def validate_year(cls, year):
        if year > datetime.now().year:
            raise ValidationError("Year cant be more than current year")
        return year


class TitleDB(TitleCreate):
    id: int
    reviews_score: float
    description: Optional[str]


class ReviewCreate(BaseModel):
    text: str
    score: conint(ge=1, le=10)


class ReviewDB(ReviewCreate):
    id: int
    author: str
    pub_date: datetime


class CommentCreate(BaseModel):
    text: str


class CommentDB(CommentCreate):
    id: int
    author: str
    pub_date: datetime
