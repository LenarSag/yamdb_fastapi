from typing import Union, Optional, Sequence, Any

from sqlalchemy import select, or_, extract
from sqlalchemy.engine import Row
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession

from models.review import Review, Title, Genre, Category
from schemas.review_schema import TitleCreate


async def create_title(
    session: AsyncSession,
    title_data: TitleCreate,
    category_id: int,
    genres: list[Genre],
) -> Optional[Title]:
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


async def get_title_by_id(session: AsyncSession, title_id: int) -> Optional[Title]:
    query = select(Title).filter_by(id=title_id)
    result = await session.execute(query)
    return result.scalars().first()


async def get_title_by_id_with_avg_score(
    session: AsyncSession, title_id: int
) -> Row[tuple[Title, Any]]:
    query = (
        select(Title, func.avg(Review.score).label("avg_score"))
        .outerjoin(Review, Review.title_id == Title.id)
        .options(selectinload(Title.genres), selectinload(Title.category))
        .filter(Title.id == title_id)
        .group_by(Title.id)
    )
    result = await session.execute(query)
    title_with_avg_score = result.first()
    if title_with_avg_score:
        return title_with_avg_score
    return None


async def get_titles_with_avg_score(
    session: AsyncSession, searching_filters: dict[str, Union[str, int, None]]
) -> Sequence[Row[tuple[Title, Any]]]:
    query = (
        select(Title, func.avg(Review.score).label("avg_score"))
        .outerjoin(Review, Review.title_id == Title.id)
        .options(selectinload(Title.genres), selectinload(Title.category))
        .group_by(Title.id)
    )
    filters = []
    name = searching_filters.get("name")
    genres = searching_filters.get("genres")
    category = searching_filters.get("category")
    year = searching_filters.get("year")
    if name:
        filters.append(Title.name.ilike(f"%{name}%"))
    if genres:
        genre_filters = [Genre.name.like(f"%{genre}%") for genre in genres.split(",")]
        filters.append(or_(*[Title.genres.any(filter) for filter in genre_filters]))
    if category:
        filters.append(Title.category.has(Category.name.like(f"%{category}%")))
    if year:
        filters.append(Title.year == year)
    if filters:
        query = query.where(*filters)
    result = await session.execute(query)
    return result.all()


"""
filters = []
    
    if genres:
        filters.append(Title.genres.any(Genre.id.in_(genres))))
        
    if category:
        filters.append(Title.category_id == category)
        
    if year:
        filters.append(func.extract('year', Title.release_date) == year)
        
    if name:
        filters.append(Title.name.ilike(f"%{name}%"))
    
    if filters:
        query = query.where(and_(*filters))
    
    result = await session.execute(query)
    return result.all()

"""


async def update_title_info(
    session: AsyncSession,
    db_title: Title,
    new_title_data: TitleCreate,
    new_category_id: int,
    new_genres: list[Genre],
) -> Optional[Title]:
    db_title.name = new_title_data.name
    db_title.year = new_title_data.year
    db_title.description = new_title_data.description
    db_title.category_id = new_category_id
    db_title.genres = new_genres
    await session.commit()

    query = (
        select(Title)
        .filter_by(id=db_title.id)
        .options(selectinload(Title.genres), selectinload(Title.category))
    )
    result = await session.execute(query)
    return result.scalars().first()


async def delete_title(session: AsyncSession, title_db: Title) -> bool:
    await session.delete(title_db)
    await session.commit()
    return True
