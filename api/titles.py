from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Response, status
from fastapi.responses import JSONResponse
from fastapi_pagination import Page, add_pagination, paginate
from sqlalchemy.ext.asyncio import AsyncSession

from crud.genres_repository import get_genre_by_slug
from crud.titles_repository import (
    create_title,
    delete_title,
    get_title_by_id,
    get_title_by_id_with_avg_score,
    get_titles_with_avg_score,
    update_title_info,
)
from crud.user_repository import get_user_by_id
from crud.category_repository import (
    get_category_by_slug,
)
from db.database import get_session
from models.review import Category, Genre, Title
from schemas.review_schema import CategoryBase, TitleCreate, TitleOut, GenreBase
from schemas.user_schema import UserAuth
from security.security import get_user_from_token
from security.user_permissions import is_admin
from api.reviews import reviewsrouter


titlesrouter = APIRouter()


async def get_title_with_score_or_404(
    session: AsyncSession, title_id: int
) -> tuple[Title, Optional[float]]:
    result = await get_title_by_id_with_avg_score(session, title_id)
    if not result:
        raise HTTPException(
            detail="Title not found", status_code=status.HTTP_404_NOT_FOUND
        )
    title, avg_score = result
    return title, avg_score


async def get_category_or_400(session: AsyncSession, slug: str) -> Category:
    category = await get_category_by_slug(session, slug)
    if not category:
        raise HTTPException(
            detail="Category not found",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return category


async def get_genres_or_400(session: AsyncSession, genres: list[str]) -> list[Genre]:
    list_of_genres: list[Genre] = []
    for genre_slug in genres:
        genre = await get_genre_by_slug(session, genre_slug)
        if not genre:
            raise HTTPException(
                detail=f"Genre: {genre_slug} not found",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        list_of_genres.append(genre)
    return list_of_genres


@titlesrouter.post("/", response_model=TitleOut)
async def create_new_title(
    title_data: TitleCreate,
    session: AsyncSession = Depends(get_session),
    user_auth_data: UserAuth = Depends(get_user_from_token),
):
    request_user = await get_user_by_id(session, user_auth_data.id)
    permission = is_admin(request_user)
    if permission:
        category = await get_category_or_400(session, title_data.category)
        list_of_genres = await get_genres_or_400(session, title_data.genre)
        new_title = await create_title(session, title_data, category.id, list_of_genres)

        title_out = TitleOut(
            name=new_title.name,
            year=new_title.year,
            rating=None,
            description=new_title.description,
            genres=[
                GenreBase(name=genre.name, slug=genre.slug)
                for genre in new_title.genres
            ],
            category=CategoryBase(
                name=new_title.category.name, slug=new_title.category.slug
            ),
        )

        return JSONResponse(
            content=title_out.model_dump(), status_code=status.HTTP_201_CREATED
        )


@titlesrouter.get("/", response_model=Page[TitleOut])
async def get_all_titles(session: AsyncSession = Depends(get_session)):
    titles_with_scores = await get_titles_with_avg_score(session)
    titles_out = [
        TitleOut(
            name=title.name,
            year=title.year,
            rating=avg_score,
            description=title.description,
            genres=[
                GenreBase(name=genre.name, slug=genre.slug) for genre in title.genres
            ],
            category=CategoryBase(name=title.category.name, slug=title.category.slug),
        )
        for title, avg_score in titles_with_scores
    ]

    return paginate(titles_out)


@titlesrouter.get("/{title_id}/", response_model=TitleOut)
async def get_title(
    title_id: int,
    session: AsyncSession = Depends(get_session),
):
    title, avg_score = await get_title_with_score_or_404(session, title_id)
    title_out = TitleOut(
        name=title.name,
        year=title.year,
        rating=avg_score,
        description=title.description,
        genres=[GenreBase(name=genre.name, slug=genre.slug) for genre in title.genres],
        category=CategoryBase(name=title.category.name, slug=title.category.slug),
    )

    return title_out


@titlesrouter.patch("/{title_id}/", response_model=TitleOut)
async def update_title(
    title_id: int,
    title_data: TitleCreate,
    session: AsyncSession = Depends(get_session),
    user_auth_data: UserAuth = Depends(get_user_from_token),
):
    request_user = await get_user_by_id(session, user_auth_data.id)
    permission = is_admin(request_user)
    if permission:
        title_to_update, avg_score = await get_title_with_score_or_404(
            session, title_id
        )
        category = await get_category_or_400(session, title_data.category)
        list_of_genres = await get_genres_or_400(session, title_data.genre)
        updated_title = await update_title_info(
            session, title_to_update, title_data, category.id, list_of_genres
        )

        title_out = TitleOut(
            name=updated_title.name,
            year=updated_title.year,
            rating=avg_score,
            description=updated_title.description,
            genres=[
                GenreBase(name=genre.name, slug=genre.slug)
                for genre in updated_title.genres
            ],
            category=CategoryBase(
                name=updated_title.category.name, slug=updated_title.category.slug
            ),
        )

        return title_out


@titlesrouter.delete("/{title_id}/")
async def delete_title_by_id(
    title_id: int,
    session: AsyncSession = Depends(get_session),
    user_auth_data: UserAuth = Depends(get_user_from_token),
):
    request_user = await get_user_by_id(session, user_auth_data.id)
    permission = is_admin(request_user)
    if permission:
        title = await get_title_by_id(session, title_id)
        if not title:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Title not found!"
            )
        deleted = await delete_title(session, title)
        if deleted:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        raise HTTPException(
            detail="Couldnt delete, try again later",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


titlesrouter.include_router(reviewsrouter, prefix="/{title_id}/reviews")

add_pagination(titlesrouter)
