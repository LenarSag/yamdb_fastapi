from fastapi import APIRouter, HTTPException, Response, Depends, Path, status

from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from crud.reviews_repository import review_exists, create_review
from crud.user_repository import get_user_by_username

from db.database import get_session
from models.user import User
from schemas.review_schema import ReviewCreate, ReviewOut
from schemas.user_schema import UserAuth
from security.security import get_user_from_token


reviewsrouter = APIRouter()


async def get_user_or_401(session: AsyncSession, username: str) -> User:
    request_user = await get_user_by_username(session, username)
    if not request_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please, login again"
        )
    return request_user


@reviewsrouter.post("/", response_model=ReviewOut)
async def create_new_review(
    review_data: ReviewCreate,
    title_id: int = Path(..., title="The id of the title"),
    session: AsyncSession = Depends(get_session),
    user_auth_data: UserAuth = Depends(get_user_from_token),
):
    request_user = await get_user_or_401(session, user_auth_data.username)
    review = await review_exists(session, request_user.id, title_id)
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
