from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.review import Genre
from schemas.review_schema import GenreBase


async def create_genre(session: AsyncSession, category_data: GenreBase) -> Genre:
    db_category = Genre(**category_data.model_dump())
    session.add(db_category)
    await session.commit()
    await session.refresh(db_category)
    return db_category


async def get_genre_by_slug(session: AsyncSession, slug: str) -> Genre:
    query = select(Genre).filter_by(slug=slug)
    result = await session.execute(query)
    return result.scalars().first()


async def get_genres(session: AsyncSession) -> list[Genre]:
    query = select(Genre)
    result = await session.execute(query)
    return result.scalars().all()


async def delete_genre(session: AsyncSession, category_db: Genre):
    await session.delete(category_db)
    await session.commit()
    return True
