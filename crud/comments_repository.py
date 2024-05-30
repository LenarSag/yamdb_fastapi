from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import exists
from sqlalchemy.ext.asyncio import AsyncSession

from models.review import Comment
from schemas.review_schema import CommentCreate


async def create_review(
    session: AsyncSession, comment_data: CommentCreate, author_id: int, review_id: int
) -> Optional[Comment]:
    db_comment = Comment(
        **comment_data.model_dump(), author_id=author_id, review_id=review_id
    )
    session.add(db_comment)
    await session.commit()
    await session.refresh(db_comment)

    query = (
        select(Comment)
        .filter_by(id=db_comment.id)
        .options(selectinload(Comment.author))
    )
    result = await session.execute(query)
    return result.scalars().first()


# async def review_exists(session: AsyncSession, author_id: int, title_id: int):
#     subquery = select(
#         exists().where(Review.author_id == author_id, Review.title_id == title_id)
#     )

#     result = await session.execute(subquery)
#     return result.scalar()


async def get_comments(session: AsyncSession, review_id: int) -> Sequence[Comment]:
    query = (
        select(Comment)
        .filter_by(review_id=review_id)
        .options(selectinload(Comment.author))
    )
    result = await session.execute(query)
    return result.scalars().all()


async def get_comment_by_id(
    session: AsyncSession, comment_id: int
) -> Optional[Comment]:
    query = (
        select(Comment).filter_by(id=comment_id).options(selectinload(Comment.author))
    )
    result = await session.execute(query)
    return result.scalars().first()


async def update_review_info(
    session: AsyncSession, comment_db: Comment, new_comment_data: CommentCreate
) -> Comment:
    comment_db.text = new_comment_data.text
    await session.commit()
    await session.refresh(comment_db)
    return comment_db


async def delete_review(session: AsyncSession, comment_db: Comment) -> bool:
    await session.delete(comment_db)
    await session.commit()
    return True
