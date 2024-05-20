from typing import Union
from models.review import Review, Comment
from models.user import User


def is_admin(user: User) -> bool:
    return user.is_admin or user.is_superuser


def is_moderator(user: User) -> bool:
    return user.is_moderator


def is_author(author_id: int, obj: Union[Review, Comment]) -> bool:
    return author_id == obj.author_id
