from typing import Optional, Union
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from schemas.user_schema import UserCreate, UserBase


async def create_user(
    session: AsyncSession,
    user_data: Union[UserCreate, UserBase],
    code: Optional[str] = None,
) -> User:
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


async def get_users(session: AsyncSession) -> list[User]:
    query = select(User)
    result = await session.execute(query)
    return result.scalars().all()


async def update_user_info(
    session: AsyncSession, db_user: User, new_user_data: UserBase
) -> User:
    db_user.username = new_user_data.username
    db_user.email = new_user_data.email
    db_user.first_name = new_user_data.first_name
    db_user.last_name = new_user_data.last_name
    db_user.bio = new_user_data.bio
    db_user.role = new_user_data.role

    await session.commit()
    await session.refresh(db_user)
    return db_user


async def update_confirmation_code(
    session: AsyncSession, db_user: User, hashed_code: str
) -> None:
    db_user.confirmation_code = hashed_code
    await session.commit()
    await session.refresh(db_user)


async def delete_user_from_db(session: AsyncSession, db_user: User) -> bool:
    await session.delete(db_user)
    await session.commit()
    return True
