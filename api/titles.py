from fastapi import APIRouter, HTTPException, Depends, Response, status
from fastapi.responses import JSONResponse
from fastapi_pagination import Page, add_pagination, paginate
from sqlalchemy.ext.asyncio import AsyncSession

from crud.user_repository import get_user_by_username
from crud.category_repository import (
    create_category,
    delete_category,
    get_categories,
    get_category_by_slug,
)
from db.database import get_session
from models.review import Title
from models.user import User
from schemas.review_schema import CategoryBase, TitleCreate
from schemas.user_schema import UserAuth
from security.security import get_user_from_token
from security.user_permissions import is_admin


titlesrouter = APIRouter()


@titlesrouter.post("/", response_model=TitleCreate)
async def create_new_category(
    title_data: TitleCreate,
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
        title = await get_category_by_slug(session, title_data.slug)
        if title:
            raise HTTPException(
                detail="Slug should be unique! Choose another slug",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        new_category = await create_category(session, category_data)
        category = CategoryBase.model_validate(new_category)

        return JSONResponse(
            content=category.model_dump(), status_code=status.HTTP_201_CREATED
        )


@titlesrouter.get("/", response_model=Page[CategoryBase])
async def get_all_categories(session: AsyncSession = Depends(get_session)):
    categories = await get_categories(session)
    return paginate(categories)


@titlesrouter.delete("/{slug}/")
async def delete_category_by_slug(
    slug: str,
    session: AsyncSession = Depends(get_session),
    user_auth_data: UserAuth = Depends(get_user_from_token),
):
    request_user = await get_user_by_username(session, user_auth_data.username)
    if not request_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please, login again"
        )

    permission = has_rights_or_unauthorized(request_user)
    if permission:
        category = await get_category_by_slug(session, slug)
        if not category:
            raise HTTPException(
                detail="Category not found", status_code=status.HTTP_404_NOT_FOUND
            )
        deleted = await delete_category(session, category)
        if deleted:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        raise HTTPException(
            detail="Couldnt delete, try again later",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


add_pagination(categoryrouter)
