from fastapi import APIRouter, HTTPException, Response, Depends, Path, status
from fastapi.responses import JSONResponse
from fastapi_pagination import Page, add_pagination, paginate
from sqlalchemy.ext.asyncio import AsyncSession

from api.comments import commentsrouter
from crud.reviews_repository import (
    delete_review,
    get_review_by_id,
    get_reviews,
    review_exists,
    create_review,
    update_review_info,
)
from crud.titles_repository import get_title_by_id
from crud.user_repository import get_user_by_id
from db.database import get_session
from models.review import Review, Title
from schemas.review_schema import ReviewCreate, ReviewOut
from schemas.user_schema import UserAuth
from security.security import get_user_from_token
from security.user_permissions import is_admin_moderator_or_author


reviewsrouter = APIRouter()


async def get_review_or_404(session: AsyncSession, review_id: int) -> Review:
    review = await get_review_by_id(session, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found!"
        )
    return review


async def get_title_or_404(session: AsyncSession, title_id: int) -> Title:
    title = await get_title_by_id(session, title_id)
    if not title:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Title not found!"
        )
    return title


@reviewsrouter.post("/", response_model=ReviewOut)
async def create_new_review(
    review_data: ReviewCreate,
    title_id: int = Path(..., title="The id of the title"),
    session: AsyncSession = Depends(get_session),
    user_auth_data: UserAuth = Depends(get_user_from_token),
):
    request_user = await get_user_by_id(session, user_auth_data.id)
    title = await get_title_or_404(session, title_id)
    review = await review_exists(session, request_user.id, title.id)
    if review:
        raise HTTPException(
            detail="You already reviewed this title",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    new_review = await create_review(session, review_data, request_user.id, title_id)
    review_out = ReviewOut(
        id=new_review.id,
        text=new_review.text,
        score=new_review.score,
        author=new_review.author.username,
        pub_date=new_review.pub_date,
    )

    response_content = review_out.model_dump()
    # Преобразуем datetime в строку ISO 8601
    response_content["pub_date"] = review_out.pub_date.isoformat()

    return JSONResponse(
        content=response_content,
        status_code=status.HTTP_201_CREATED,
    )


@reviewsrouter.get("/", response_model=Page[ReviewOut])
async def get_all_reviews(
    title_id: int = Path(..., title="The id of the title"),
    session: AsyncSession = Depends(get_session),
):
    title = await get_title_or_404(session, title_id)
    reviews = await get_reviews(session, title.id)
    reviews_out = [
        ReviewOut(
            id=review.id,
            text=review.text,
            score=review.score,
            author=review.author.username,
            pub_date=review.pub_date,
        )
        for review in reviews
    ]
    return paginate(reviews_out)


@reviewsrouter.get("/{review_id}/", response_model=ReviewOut)
async def get_review(
    review_id: int,
    session: AsyncSession = Depends(get_session),
):
    review = await get_review_or_404(session, review_id)
    review_out = ReviewOut(
        id=review.id,
        text=review.text,
        score=review.score,
        author=review.author.username,
        pub_date=review.pub_date,
    )

    return review_out


@reviewsrouter.patch("/{review_id}/", response_model=ReviewOut)
async def update_review(
    review_id: int,
    new_review_data: ReviewCreate,
    session: AsyncSession = Depends(get_session),
    user_auth_data: UserAuth = Depends(get_user_from_token),
):
    review_to_update = await get_review_or_404(session, review_id)
    request_user = await get_user_by_id(session, user_auth_data.id)
    permission = is_admin_moderator_or_author(request_user, review_to_update)
    if permission:
        updated_review = await update_review_info(
            session,
            review_to_update,
            new_review_data,
        )
        review_out = ReviewOut(
            id=updated_review.id,
            text=updated_review.text,
            score=updated_review.score,
            author=updated_review.author.username,
            pub_date=updated_review.pub_date,
        )

        return review_out


@reviewsrouter.delete("/{review_id}/")
async def delete_review_by_id(
    review_id: int,
    session: AsyncSession = Depends(get_session),
    user_auth_data: UserAuth = Depends(get_user_from_token),
):
    review_to_delete = await get_review_or_404(session, review_id)
    request_user = await get_user_by_id(session, user_auth_data.id)
    permission = is_admin_moderator_or_author(request_user, review_to_delete)
    if permission:
        deleted = await delete_review(session, review_to_delete)
        if deleted:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        raise HTTPException(
            detail="Couldnt delete, try again later",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


reviewsrouter.include_router(commentsrouter, prefix="/{review_id}/comments")

add_pagination(reviewsrouter)
