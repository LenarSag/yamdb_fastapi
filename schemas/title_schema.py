from typing import Union
from datetime import datetime

from pydantic import BaseModel, constr, field_validator, ValidationError

# from config import MAX_SLUG_LENGTH, MIN_SLUG_LENGTH


# class CategoryCreate(BaseModel):
#     name: str
#     slug: constr(
#         min_length=MIN_SLUG_LENGTH,
#         max_length=MAX_SLUG_LENGTH,
#     )


# class Genre(BaseModel):
#     name: str
#     slug: constr(
#         min_length=MIN_SLUG_LENGTH,
#         max_length=MAX_SLUG_LENGTH,
#     )


class TitleCreate(BaseModel):
    name: str
    year: int
    genre: str
    category: str

    @field_validator("year")
    def validate_year(cls, year):
        if year > datetime.now().year:
            raise ValidationError("Year cant be more than current year")
