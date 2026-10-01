from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewUpdate
from app.services.review import (
    ResourceNotFoundError,
    ReviewNotFoundError,
    ReviewService,
)

router = APIRouter(prefix="/reviews", tags=["Reviews"])
service = ReviewService()

DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[ReviewResponse])
def list_reviews(
    db: DbSession,
    product_id: int | None = Query(default=None),
    customer_id: int | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    return service.list_reviews(
        db,
        product_id=product_id,
        customer_id=customer_id,
        skip=skip,
        limit=limit,
    )


@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(review_id: int, db: DbSession):
    try:
        return service.get_review(db, review_id)
    except ReviewNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_review(data: ReviewCreate, db: DbSession):
    try:
        return service.create_review(db, data)
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(review_id: int, data: ReviewUpdate, db: DbSession):
    try:
        return service.update_review(db, review_id, data)
    except ReviewNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(review_id: int, db: DbSession):
    try:
        service.delete_review(db, review_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ReviewNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
