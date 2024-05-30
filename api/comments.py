from fastapi import APIRouter, HTTPException, Response, Depends, Path, status
from fastapi.responses import JSONResponse
from fastapi_pagination import Page, add_pagination, paginate
from sqlalchemy.ext.asyncio import AsyncSession

from crud.comments_repository import (
    delete_comment,
    get_comment_by_id,
    get_comments,
    create_comment,
    update_comment_info,
)
from crud.reviews_repository import get_review_by_id
from crud.user_repository import get_user_by_id
from db.database import get_session
from models.review import Comment, Review
from schemas.review_schema import CommentCreate, CommentOut
from schemas.user_schema import UserAuth
from security.security import get_user_from_token
from security.user_permissions import is_admin_moderator_or_author


commentsrouter = APIRouter()


async def get_comment_or_404(session: AsyncSession, comment_id: int) -> Comment:
    comment = await get_comment_by_id(session, comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found!"
        )
    return comment


async def get_review_or_404(session: AsyncSession, review_id: int) -> Review:
    review = await get_review_by_id(session, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Title not found!"
        )
    return review


@commentsrouter.post("/", response_model=CommentOut)
async def create_new_comment(
    comment_data: CommentCreate,
    review_id: int = Path(..., review="The id of the review"),
    session: AsyncSession = Depends(get_session),
    user_auth_data: UserAuth = Depends(get_user_from_token),
):
    request_user = await get_user_by_id(session, user_auth_data.id)
    review = await get_review_or_404(session, review_id)
    new_comment = await create_comment(
        session, comment_data, request_user.id, review.id
    )
    comment_out = CommentOut(
        id=new_comment.id,
        text=new_comment.text,
        author=new_comment.author.username,
        pub_date=new_comment.pub_date,
    )

    response_content = comment_out.model_dump()
    # Преобразуем datetime в строку ISO 8601
    response_content["pub_date"] = comment_out.pub_date.isoformat()

    return JSONResponse(
        content=response_content,
        status_code=status.HTTP_201_CREATED,
    )


@commentsrouter.get("/", response_model=Page[CommentOut])
async def get_all_comments(
    review_id: int = Path(..., review="The id of the review"),
    session: AsyncSession = Depends(get_session),
):
    review = await get_review_or_404(session, review_id)
    comments = await get_comments(session, review.id)
    comments_out = [
        CommentOut(
            id=comment.id,
            text=comment.text,
            author=comment.author.username,
            pub_date=comment.pub_date,
        )
        for comment in comments
    ]
    return paginate(comments_out)


@commentsrouter.get("/{comment_id}/", response_model=CommentOut)
async def get_review(
    comment_id: int,
    session: AsyncSession = Depends(get_session),
):
    comment = await get_comment_or_404(session, comment_id)
    comment_out = CommentOut(
        id=comment.id,
        text=comment.text,
        author=comment.author.username,
        pub_date=comment.pub_date,
    )

    return comment_out


@commentsrouter.patch("/{comment_id}/", response_model=CommentOut)
async def update_review(
    comment_id: int,
    new_comment_data: CommentCreate,
    session: AsyncSession = Depends(get_session),
    user_auth_data: UserAuth = Depends(get_user_from_token),
):
    comment_to_update = await get_comment_or_404(session, comment_id)
    request_user = await get_user_by_id(session, user_auth_data.id)
    permission = is_admin_moderator_or_author(request_user, comment_to_update)
    if permission:
        updated_comment = await update_comment_info(
            session,
            comment_to_update,
            new_comment_data,
        )
        review_out = CommentOut(
            id=updated_comment.id,
            text=updated_comment.text,
            author=updated_comment.author.username,
            pub_date=updated_comment.pub_date,
        )

        return review_out


@commentsrouter.delete("/{comment_id}/")
async def delete_review_by_id(
    comment_id: int,
    session: AsyncSession = Depends(get_session),
    user_auth_data: UserAuth = Depends(get_user_from_token),
):
    comment_to_delete = await get_comment_or_404(session, comment_id)
    request_user = await get_user_by_id(session, user_auth_data.id)
    permission = is_admin_moderator_or_author(request_user, comment_to_delete)
    if permission:
        deleted = await delete_comment(session, comment_to_delete)
        if deleted:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        raise HTTPException(
            detail="Couldnt delete, try again later",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


add_pagination(commentsrouter)
