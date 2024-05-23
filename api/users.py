from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi_pagination import Page, add_pagination, paginate
from sqlalchemy.ext.asyncio import AsyncSession


from models.user import User
from schemas.user_schema import UserAuth, UserBase, UserDB
from db.database import get_session
from crud.user_repository import (
    create_user,
    get_user_by_username,
    get_user_by_email,
    get_users,
)
from security.security import get_user_from_token
from security.user_roles import is_admin


usersrouter = APIRouter()


def has_rights_or_unauthorized(user: User):
    if not is_admin(user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Only for admins!"
        )
    return True


@usersrouter.get("/", response_model=Page[UserDB])
async def get_all_user(
    session: AsyncSession = Depends(get_session),
    user_auth_data: UserAuth = Depends(get_user_from_token),
):
    user = await get_user_by_username(session, user_auth_data.username)
    permission = has_rights_or_unauthorized(user)
    if permission:
        users = await get_users(session)
        return paginate(users)


@usersrouter.post("/", response_model=UserDB)
async def create_new_user(
    new_user_data: UserBase,
    session: AsyncSession = Depends(get_session),
    user_auth_data: UserAuth = Depends(get_user_from_token),
):
    request_user = await get_user_by_username(session, user_auth_data.username)
    permission = has_rights_or_unauthorized(request_user)
    if permission:
        new_user_by_username = await get_user_by_username(
            session, new_user_data.username
        )
        new_user_by_email = await get_user_by_email(session, new_user_data.email)

        if new_user_by_username:
            raise HTTPException(
                detail="Username already taken", status_code=status.HTTP_400_BAD_REQUEST
            )
        if new_user_by_email:
            raise HTTPException(
                detail="Email already registered",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        new_user = await create_user(session, new_user_data)
        user = UserDB.model_validate(new_user)

        return JSONResponse(
            content=user.model_dump(), status_code=status.HTTP_201_CREATED
        )


@usersrouter.get("/{username}/", response_model=UserDB)
async def get_user_for_admin(
    username: str,
    session: AsyncSession = Depends(get_session),
    user_auth_data: UserAuth = Depends(get_user_from_token),
):
    request_user = await get_user_by_username(session, user_auth_data.username)
    permission = has_rights_or_unauthorized(request_user)
    if permission:
        user_model = await get_user_by_username(session, username)
        user = UserDB.model_validate(user_model)
        return user


add_pagination(usersrouter)
