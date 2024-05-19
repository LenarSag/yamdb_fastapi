import uuid

from fastapi import APIRouter, HTTPException, Response, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.user_schema import UserCreate
from db.database import get_session
from crud.user_repository import (
    create_user,
    get_user_by_username,
    get_user_by_email,
    update_confirmation_code,
)
from utils.send_email import send_confirmation_code


loginroute = APIRouter()


@loginroute.post("/signup/", response_model=UserCreate)
async def signup_and_get_confirmation_code(
    user_data: UserCreate = Depends(),
    session: AsyncSession = Depends(get_session),
):
    user_by_username = await get_user_by_username(session, user_data.username)
    user_by_email = await get_user_by_email(session, user_data.email)

    if user_by_username and user_by_email:
        code = str(uuid.uuid4())
        await update_confirmation_code(session, user_by_username, code)
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

    new_user = await create_user(session, user_data)
    await send_confirmation_code(new_user.email, new_user.confirmation_code)
    user = UserCreate(username=new_user.username, email=new_user.email)

    return JSONResponse(content=user.model_dump(), status_code=status.HTTP_200_OK)
