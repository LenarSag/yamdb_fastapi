from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from schemas.user_schema import UserCreate


async def create_user(session: AsyncSession, user_data: UserCreate, code: str) -> User:
    db_user = User(**user_data.model_dump(), confirmation_code=code)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def get_user_by_username(session: AsyncSession, username: str) -> User:
    query = select(User).filter_by(username=username)
    result = await session.execute(query)
    return result.scalars().first()


async def get_user_by_email(session: AsyncSession, email: str) -> User:
    query = select(User).filter_by(email=email)
    result = await session.execute(query)
    return result.scalars().first()


async def update_confirmation_code(
    session: AsyncSession, db_user: User, hashed_code: str
) -> None:
    db_user.confirmation_code = hashed_code
    await session.commit()
    await session.refresh(db_user)
