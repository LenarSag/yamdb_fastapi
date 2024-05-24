from fastapi import APIRouter, HTTPException, Depends, Response, status
from fastapi.responses import JSONResponse
from fastapi_pagination import Page, add_pagination, paginate
from sqlalchemy.ext.asyncio import AsyncSession

from crud.genres_repository import get_genre_by_slug
from crud.titles_repository import (
    create_title,
    delete_title,
    get_title_by_id,
    get_titles,
)
from crud.user_repository import get_user_by_username
from crud.category_repository import (
    get_category_by_slug,
)
from db.database import get_session
from models.review import Genre
from models.user import User
from schemas.review_schema import CategoryBase, TitleCreate, TitleOut, GenreBase
from schemas.user_schema import UserAuth
from security.security import get_user_from_token
from security.user_permissions import is_admin


titlesrouter = APIRouter()


async def user_exist_or_401(session: AsyncSession, username: str) -> User:
    request_user = await get_user_by_username(session, username)
    if not request_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please, login again"
        )
    return request_user


@titlesrouter.post("/", response_model=TitleOut)
async def create_new_title(
    title_data: TitleCreate,
    session: AsyncSession = Depends(get_session),
    user_auth_data: UserAuth = Depends(get_user_from_token),
):
    request_user = await user_exist_or_401(session, user_auth_data.username)
    permission = is_admin(request_user)
    if permission:
        category = await get_category_by_slug(session, title_data.category)
        if not category:
            raise HTTPException(
                detail="Category not found",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        list_of_genres: list[Genre] = []
        for genre_slug in title_data.genre:
            genre = await get_genre_by_slug(session, genre_slug)
            if not genre:
                raise HTTPException(
                    detail=f"Genre: {genre_slug} not found",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            list_of_genres.append(genre)

        new_title = await create_title(session, title_data, category.id, list_of_genres)

        title = TitleOut(
            name=new_title.name,
            year=new_title.year,
            rating=3.4,
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
            content=title.model_dump(), status_code=status.HTTP_201_CREATED
        )


@titlesrouter.get("/", response_model=Page[TitleOut])
async def get_all_titles(session: AsyncSession = Depends(get_session)):
    titles = await get_titles(session)
    titles_out = [
        TitleOut(
            name=title.name,
            year=title.year,
            rating=3.4,
            description=title.description,
            genres=[
                GenreBase(name=genre.name, slug=genre.slug) for genre in title.genres
            ],
            category=CategoryBase(name=title.category.name, slug=title.category.slug),
        )
        for title in titles
    ]

    return paginate(titles_out)


@titlesrouter.get("/{title_id}/", response_model=TitleOut)
async def get_title(
    title_id: int,
    session: AsyncSession = Depends(get_session),
):
    title = await get_title_by_id(session, title_id)
    if not title:
        raise HTTPException(
            detail="Title not found", status_code=status.HTTP_404_NOT_FOUND
        )
    title_out = TitleOut(
        name=title.name,
        year=title.year,
        rating=3.4,
        description=title.description,
        genres=[GenreBase(name=genre.name, slug=genre.slug) for genre in title.genres],
        category=CategoryBase(name=title.category.name, slug=title.category.slug),
    )

    return JSONResponse(content=title_out.model_dump(), status_code=status.HTTP_200_OK)


@titlesrouter.delete("/{title_id}/")
async def delete_title_by_id(
    title_id: int,
    session: AsyncSession = Depends(get_session),
    user_auth_data: UserAuth = Depends(get_user_from_token),
):
    request_user = await user_exist_or_401(session, user_auth_data.username)
    permission = is_admin(request_user)
    if permission:
        title = await get_title_by_id(session, title_id)
        if not title:
            raise HTTPException(
                detail="Title not found", status_code=status.HTTP_404_NOT_FOUND
            )
        deleted = await delete_title(session, title)
        if deleted:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        raise HTTPException(
            detail="Couldnt delete, try again later",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


add_pagination(titlesrouter)
