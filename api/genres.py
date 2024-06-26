from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Response, status
from fastapi.responses import JSONResponse
from fastapi_pagination import Page, add_pagination, paginate
from sqlalchemy.ext.asyncio import AsyncSession

from crud.user_repository import get_user_by_id
from crud.genres_repository import (
    create_genre,
    get_genre_by_slug,
    get_genres,
    delete_genre,
)
from db.database import get_session
from schemas.review_schema import GenreBase
from schemas.user_schema import UserAuth
from security.security import get_user_from_token
from security.user_permissions import is_admin


genresrouter = APIRouter()


@genresrouter.post("/", response_model=GenreBase)
async def create_new_genre(
    genre_data: GenreBase,
    session: AsyncSession = Depends(get_session),
    user_auth_data: UserAuth = Depends(get_user_from_token),
):
    request_user = await get_user_by_id(session, user_auth_data.id)
    permission = is_admin(request_user)
    if permission:
        category = await get_genre_by_slug(session, genre_data.slug)
        if category:
            raise HTTPException(
                detail="Slug should be unique! Choose another slug",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        new_genre = await create_genre(session, genre_data)
        genre = GenreBase.model_validate(new_genre)

        return JSONResponse(
            content=genre.model_dump(), status_code=status.HTTP_201_CREATED
        )


@genresrouter.get("/", response_model=Page[GenreBase])
async def get_all_genres(
    session: AsyncSession = Depends(get_session),
    filter_name: Optional[str] = Query(None),
):
    categories = await get_genres(session, filter_name)
    return paginate(categories)


@genresrouter.delete("/{slug}/")
async def delete_genre_by_slug(
    slug: str,
    session: AsyncSession = Depends(get_session),
    user_auth_data: UserAuth = Depends(get_user_from_token),
):
    request_user = await get_user_by_id(session, user_auth_data.id)
    permission = is_admin(request_user)
    if permission:
        category = await get_genre_by_slug(session, slug)
        if not category:
            raise HTTPException(
                detail="Genre not found", status_code=status.HTTP_404_NOT_FOUND
            )
        deleted = await delete_genre(session, category)
        if deleted:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        raise HTTPException(
            detail="Couldn't delete, try again later",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


add_pagination(genresrouter)
