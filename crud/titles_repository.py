from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from models.review import Title, Genre
from schemas.review_schema import TitleCreate, TitleOut, GenreBase, CategoryBase


async def create_title(
    session: AsyncSession,
    title_data: TitleCreate,
    category_id: int,
    genres: list[Genre],
) -> Title:
    db_title = Title(
        name=title_data.name,
        year=title_data.year,
        description=title_data.description,
        category_id=category_id,
    )
    db_title.genres.extend(genres)
    session.add(db_title)
    await session.commit()
    await session.refresh(db_title)

    query = (
        select(Title)
        .filter_by(name=db_title.name)
        .options(selectinload(Title.genres), selectinload(Title.category))
    )
    result = await session.execute(query)
    return result.scalars().first()


async def get_title_by_id(session: AsyncSession, title_id: int) -> Title:
    query = (
        select(Title)
        .filter_by(id=title_id)
        .options(selectinload(Title.genres), selectinload(Title.category))
    )
    result = await session.execute(query)
    return result.scalars().first()


async def get_titles(session: AsyncSession) -> list[Title]:
    query = select(Title).options(
        selectinload(Title.genres), selectinload(Title.category)
    )
    result = await session.execute(query)
    return result.scalars().all()


async def delete_title(session: AsyncSession, title_db: Title) -> bool:
    await session.delete(title_db)
    await session.commit()
    return True
