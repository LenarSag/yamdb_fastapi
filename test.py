from enum import Enum as PyEnum


class UserRoles(PyEnum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


print(UserRoles.USER.value)
