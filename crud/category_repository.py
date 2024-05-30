from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.review import Category
from schemas.review_schema import CategoryBase


async def create_category(
    session: AsyncSession, category_data: CategoryBase
) -> Category:
    db_category = Category(**category_data.model_dump())
    session.add(db_category)
    await session.commit()
    await session.refresh(db_category)
    return db_category


async def get_category_by_slug(session: AsyncSession, slug: str) -> Optional[Category]:
    query = select(Category).filter_by(slug=slug)
    result = await session.execute(query)
    return result.scalars().first()


async def get_categories(session: AsyncSession) -> Sequence[Category]:
    query = select(Category)
    result = await session.execute(query)
    return result.scalars().all()


async def delete_category(session: AsyncSession, category_db: Category) -> bool:
    await session.delete(category_db)
    await session.commit()
    return True
