from fastapi import APIRouter, HTTPException, Response, Depends, status
from fastapi.responses import JSONResponse
from fastapi_pagination import Page, add_pagination, paginate
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession


from models.user import User
from schemas.user_schema import UserAuth, UserBase, UserDB
from db.database import get_session
from crud.user_repository import (
    create_user,
    delete_user_from_db,
    get_user_by_username,
    get_user_by_email,
    get_users,
    update_user_info,
)
from security.security import get_user_from_token
from security.user_permissions import is_admin


usersrouter = APIRouter()


async def get_user_or_401(session: AsyncSession, username: str) -> User:
    request_user = await get_user_by_username(session, username)
    if not request_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please, login again"
        )
    return request_user


async def username_is_free(session: AsyncSession, username: str, method: str = "post"):
    user_by_username = await get_user_by_username(session, username)
    if user_by_username:
        raise HTTPException(
            detail="Username already taken", status_code=status.HTTP_400_BAD_REQUEST
        )
    return user_by_username


async def email_is_free(session: AsyncSession, email: EmailStr):
    user_by_email = await get_user_by_email(session, email)
    if user_by_email:
        raise HTTPException(
            detail="Email already registered",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return user_by_email


@usersrouter.get("/", response_model=Page[UserDB])
async def get_all_user(
    session: AsyncSession = Depends(get_session),
    user_auth_data: UserAuth = Depends(get_user_from_token),
):
    request_user = await get_user_by_username(session, user_auth_data.username)
    if not request_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please, login again"
        )
    permission = is_admin(request_user)
    if permission:
        users = await get_users(session)
        return paginate(users)


@usersrouter.post("/", response_model=UserDB)
async def create_new_user(
    new_user_data: UserBase,
    session: AsyncSession = Depends(get_session),
    user_auth_data: UserAuth = Depends(get_user_from_token),
):
    request_user = await get_user_or_401(session, user_auth_data.username)
    permission = is_admin(request_user)
    if permission:
        user_by_username = await get_user_by_username(session, new_user_data.username)
        if user_by_username:
            raise HTTPException(
                detail="Username already taken", status_code=status.HTTP_400_BAD_REQUEST
            )
        user_by_email = await get_user_by_email(session, new_user_data.email)
        if user_by_email:
            raise HTTPException(
                detail="Email already registered",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        new_user = await create_user(session, new_user_data)
        user = UserDB.model_validate(new_user)

        return JSONResponse(
            content=user.model_dump(), status_code=status.HTTP_201_CREATED
        )


@usersrouter.get("/me/", response_model=UserDB)
async def get_myself(
    session: AsyncSession = Depends(get_session),
    user_auth_data: UserAuth = Depends(get_user_from_token),
):
    request_user = await get_user_or_401(session, user_auth_data.username)
    user = UserDB.model_validate(request_user)
    return user


@usersrouter.patch("/me/", response_model=UserDB)
async def update_myself(
    new_user_data: UserBase,
    session: AsyncSession = Depends(get_session),
    user_auth_data: UserAuth = Depends(get_user_from_token),
):
    request_user = await get_user_or_401(session, user_auth_data.username)

    user_by_username = await get_user_by_username(session, new_user_data.username)
    user_by_email = await get_user_by_email(session, new_user_data.email)

    if user_by_username and new_user_data.username != request_user.username:
        raise HTTPException(
            detail="Username already taken", status_code=status.HTTP_400_BAD_REQUEST
        )
    if user_by_email and new_user_data.email != request_user.email:
        raise HTTPException(
            detail="Email already registered",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    new_user_data.role = request_user.role
    updated_user = await update_user_info(session, request_user, new_user_data)
    user = UserDB.model_validate(updated_user)
    return user


@usersrouter.get("/{username}/", response_model=UserDB)
async def get_user_for_admin(
    username: str,
    session: AsyncSession = Depends(get_session),
    user_auth_data: UserAuth = Depends(get_user_from_token),
):
    request_user = await get_user_or_401(session, user_auth_data.username)
    permission = is_admin(request_user)
    if permission:
        user_model = await get_user_by_username(session, username)
        if not user_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        user = UserDB.model_validate(user_model)
        return user


@usersrouter.patch("/{username}/", response_model=UserDB)
async def update_user(
    username: str,
    new_user_data: UserBase,
    session: AsyncSession = Depends(get_session),
    user_auth_data: UserAuth = Depends(get_user_from_token),
):
    request_user = await get_user_or_401(session, user_auth_data.username)
    permission = is_admin(request_user)
    if permission:
        user_to_update = await get_user_by_username(session, username)
        if not user_to_update:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        user_by_username = await get_user_by_username(session, new_user_data.username)
        user_by_email = await get_user_by_email(session, new_user_data.email)

        if user_by_username and new_user_data.username != user_to_update.username:
            raise HTTPException(
                detail="Username already taken", status_code=status.HTTP_400_BAD_REQUEST
            )
        if user_by_email and new_user_data.email != user_to_update.email:
            raise HTTPException(
                detail="Email already registered",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        updated_user = await update_user_info(session, request_user, new_user_data)
        user = UserDB.model_validate(updated_user)
        return user


@usersrouter.delete("/{username}/")
async def delete_user(
    username: str,
    session: AsyncSession = Depends(get_session),
    user_auth_data: UserAuth = Depends(get_user_from_token),
):
    request_user = await get_user_or_401(session, user_auth_data.username)
    permission = is_admin(request_user)
    if permission:
        user_to_delete = await get_user_by_username(session, username)
        if not user_to_delete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        deleted = await delete_user_from_db(session, user_to_delete)
        if deleted:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        raise HTTPException(
            detail="Couldn't delete, try again later",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


add_pagination(usersrouter)
