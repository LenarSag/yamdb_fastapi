import uuid

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession


from schemas.user_schema import UserCreate, UserGetToken
from db.database import get_session
from crud.user_repository import (
    create_user,
    get_user_by_username,
    get_user_by_email,
    update_confirmation_code,
)
from utils.send_email import send_confirmation_code
from security.security import authenticate_user, create_access_token
from security.pwd_crypt import get_hashed_code


loginroute = APIRouter()


def create_confirmation_code():
    return str(uuid.uuid4())


@loginroute.post("/signup/", response_model=UserCreate)
async def signup_and_get_confirmation_code(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    user_by_username = await get_user_by_username(session, user_data.username)
    user_by_email = await get_user_by_email(session, user_data.email)

    if user_by_username and user_by_email:
        code = create_confirmation_code()
        hashed_code = get_hashed_code(code)

        await update_confirmation_code(session, user_by_username, hashed_code)
        await send_confirmation_code(user_data.email, code)
        return JSONResponse(
            content=user_data.model_dump(), status_code=status.HTTP_200_OK
        )
    if user_by_username:
        raise HTTPException(
            detail="Username already taken", status_code=status.HTTP_400_BAD_REQUEST
        )
    if user_by_email:
        raise HTTPException(
            detail="Email already registered", status_code=status.HTTP_400_BAD_REQUEST
        )

    code = create_confirmation_code()
    hashed_code = get_hashed_code(code)

    new_user = await create_user(session, user_data, hashed_code)
    await send_confirmation_code(new_user.email, code)
    user = UserCreate(username=new_user.username, email=new_user.email)

    return JSONResponse(content=user.model_dump(), status_code=status.HTTP_200_OK)


@loginroute.post("/token/")
async def login_for_access_token(
    user_data: UserGetToken,
    session: AsyncSession = Depends(get_session),
):
    username = user_data.username
    confirmation_code = user_data.confirmation_code

    user = await authenticate_user(session, username, confirmation_code)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user)
    return {"access_token": access_token, "token_type": "bearer"}
