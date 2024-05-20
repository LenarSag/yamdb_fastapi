from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.review import Category
from schemas.review_schema import CategoryCreate


async def create_category(
    session: AsyncSession, category_data: CategoryCreate
) -> Category:
    db_category = Category(**category_data.model_dump())
    session.add(db_category)
    await session.commit()
    await session.refresh(db_category)
    return db_category
