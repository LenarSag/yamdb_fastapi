from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import exists
from sqlalchemy.ext.asyncio import AsyncSession

from models.review import Review
from schemas.review_schema import ReviewCreate


async def create_review(
    session: AsyncSession, review_data: ReviewCreate, author_id: int, title_id: int
) -> Review:
    db_review = Review(
        **review_data.model_dump(), author_id=author_id, title_id=title_id
    )
    session.add(db_review)
    await session.commit()
    await session.refresh(db_review)

    query = (
        select(Review).filter_by(id=db_review.id).options(selectinload(Review.author))
    )
    result = await session.execute(query)
    return result.scalars().first()


async def review_exists(session: AsyncSession, author_id: int, title_id: int):
    subquery = select(
        exists().where(Review.author_id == author_id, Review.title_id == title_id)
    )

    result = await session.execute(subquery)
    return result.scalar()


async def get_reviews(session: AsyncSession, title_id: int) -> list[Review]:
    query = (
        select(Review).filter_by(title_id=title_id).options(selectinload(Review.author))
    )
    result = await session.execute(query)
    return result.scalars().all()


async def get_review_by_id(session: AsyncSession, review_id: int) -> Review:
    query = select(Review).filter_by(id=review_id).options(selectinload(Review.author))
    result = await session.execute(query)
    return result.scalars().first()


async def update_review_info(
    session: AsyncSession, db_review: Review, new_review_data: ReviewCreate
) -> Review:
    db_review.text = new_review_data.text
    db_review.score = new_review_data.score
    await session.commit()
    await session.refresh(db_review)
    return db_review


async def delete_review(session: AsyncSession, review_db: Review) -> bool:
    await session.delete(review_db)
    await session.commit()
    return True


# async def get_category_by_slug(session: AsyncSession, slug: str) -> Category:
#     query = select(Category).filter_by(slug=slug)
#     result = await session.execute(query)
#     return result.scalars().first()


# async def get_categories(session: AsyncSession) -> list[Category]:
#     query = select(Category)
#     result = await session.execute(query)
#     return result.scalars().all()


# async def delete_category(session: AsyncSession, category_db: Category) -> bool:
#     await session.delete(category_db)
#     await session.commit()
#     return True
