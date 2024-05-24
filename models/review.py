from datetime import datetime

from typing import Optional
from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Integer,
    DateTime,
    Table,
    func,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import validates

from config import MAX_FIELD_LENGTH, MAX_SLUG_LENGTH
from models.base import Base


genre_title = Table(
    "genre_title",
    Base.metadata,
    Column("genre_id", ForeignKey("genre.id", ondelete="CASCADE"), primary_key=True),
    Column("title_id", ForeignKey("title.id", ondelete="CASCADE"), primary_key=True),
)


class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(MAX_FIELD_LENGTH))
    slug: Mapped[str] = mapped_column(String(MAX_SLUG_LENGTH), unique=True)

    titles: Mapped[list["Title"]] = relationship("Title", back_populates="category")


class Genre(Base):
    __tablename__ = "genre"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(MAX_FIELD_LENGTH))
    slug: Mapped[str] = mapped_column(String(MAX_SLUG_LENGTH), unique=True)

    titles: Mapped[list["Title"]] = relationship(
        secondary=genre_title, back_populates="genres"
    )


class Title(Base):
    __tablename__ = "title"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(MAX_FIELD_LENGTH))
    year: Mapped[int]
    description: Mapped[Optional[str]]
    category_id: Mapped[int] = mapped_column(
        ForeignKey("category.id", ondelete="SET NULL"), nullable=True
    )
    genres: Mapped[list["Genre"]] = relationship(
        secondary=genre_title, back_populates="titles"
    )

    category: Mapped["Category"] = relationship("Category", back_populates="titles")
    reviews: Mapped[list["Review"]] = relationship(
        "Review", back_populates="title", cascade="all, delete-orphan"
    )

    @validates("year")
    def validate_year(self, key, value):
        current_year = datetime.now().year
        if value > current_year:
            raise ValueError("Year cant be more than current year")
        return value


class Review(Base):
    __tablename__ = "review"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str]
    score: Mapped[int] = mapped_column(
        Integer, CheckConstraint("score >= 1 AND score <= 10"), nullable=False
    )
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    title_id: Mapped[int] = mapped_column(ForeignKey("title.id"))
    pub_date: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    author = relationship("User", back_populates="reviews")
    title: Mapped["Title"] = relationship("Title", back_populates="reviews")
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="review", cascade="all, delete-orphan"
    )


class Comment(Base):
    __tablename__ = "comment"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    review_id: Mapped[int] = mapped_column(ForeignKey("review.id"))
    pub_date: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    author = relationship("User", back_populates="comments")
    review: Mapped["Review"] = relationship("Review", back_populates="comments")
