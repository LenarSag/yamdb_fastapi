from typing import Optional, Sequence

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


async def get_genre_by_slug(session: AsyncSession, slug: str) -> Optional[Genre]:
    query = select(Genre).filter_by(slug=slug)
    result = await session.execute(query)
    return result.scalars().first()


async def get_genres(
    session: AsyncSession, name: Optional[str] = None
) -> Sequence[Genre]:
    query = select(Genre)
    if name:
        query.where(Genre.name.ilike(f"%{name}%"))
    result = await session.execute(query)
    return result.scalars().all()


async def delete_genre(session: AsyncSession, category_db: Genre) -> bool:
    await session.delete(category_db)
    await session.commit()
    return True
