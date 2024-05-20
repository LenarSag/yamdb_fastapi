from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from crud.user_repository import get_user_by_username
from crud.category_repository import create_category
from db.database import get_session
from schemas.review_schema import CategoryCreate
from schemas.user_schema import UserAuth
from security.security import get_user_from_token
from security.user_roles import is_admin


categoryrouter = APIRouter()


@categoryrouter.post("/")
async def create_new_category(
    category_data: CategoryCreate,
    session: AsyncSession = Depends(get_session),
    user_auth_data: UserAuth = Depends(get_user_from_token),
):
    user = await get_user_by_username(session, user_auth_data.username)
    if not is_admin(user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Only for admins!"
        )
    new_category = await create_category(session, category_data)

    # return JSONResponse(content=new_category, status_code=status.HTTP_200_OK)
    return new_category
