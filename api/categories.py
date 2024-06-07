from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Response, status
from fastapi.responses import JSONResponse
from fastapi_pagination import Page, add_pagination, paginate
from sqlalchemy.ext.asyncio import AsyncSession

from crud.user_repository import get_user_by_id
from crud.category_repository import (
    create_category,
    delete_category,
    get_categories,
    get_category_by_slug,
)
from db.database import get_session
from schemas.review_schema import CategoryBase
from schemas.user_schema import UserAuth
from security.security import get_user_from_token
from security.user_permissions import is_admin


categoryrouter = APIRouter()


@categoryrouter.post("/", response_model=CategoryBase)
async def create_new_category(
    category_data: CategoryBase,
    session: AsyncSession = Depends(get_session),
    user_auth_data: UserAuth = Depends(get_user_from_token),
):
    request_user = await get_user_by_id(session, user_auth_data.id)
    permission = is_admin(request_user)
    if permission:
        category = await get_category_by_slug(session, category_data.slug)
        if category:
            raise HTTPException(
                detail="Slug should be unique! Choose another slug",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        new_category = await create_category(session, category_data)
        category = CategoryBase.model_validate(new_category)

        return JSONResponse(
            content=category.model_dump(), status_code=status.HTTP_201_CREATED
        )


@categoryrouter.get("/", response_model=Page[CategoryBase])
async def get_all_categories(
    session: AsyncSession = Depends(get_session),
    filter_name: Optional[str] = Query(None),
):
    categories = await get_categories(session, filter_name)
    return paginate(categories)


@categoryrouter.delete("/{slug}/")
async def delete_category_by_slug(
    slug: str,
    session: AsyncSession = Depends(get_session),
    user_auth_data: UserAuth = Depends(get_user_from_token),
):
    request_user = await get_user_by_id(session, user_auth_data.id)
    permission = is_admin(request_user)
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
