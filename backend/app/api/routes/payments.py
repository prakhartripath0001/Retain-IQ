from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentUpdate
from app.services.payment import (
    DuplicatePaymentError,
    OrderNotFoundError,
    PaymentNotFoundError,
    PaymentService,
)

router = APIRouter(prefix="/payments", tags=["Payments"])
service = PaymentService()

DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[PaymentResponse])
def list_payments(
    db: DbSession,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    return service.list_payments(db, skip=skip, limit=limit)


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int, db: DbSession):
    try:
        return service.get_payment(db, payment_id)
    except PaymentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_payment(data: PaymentCreate, db: DbSession):
    try:
        return service.create_payment(db, data)
    except OrderNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DuplicatePaymentError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.put("/{payment_id}", response_model=PaymentResponse)
def update_payment(payment_id: int, data: PaymentUpdate, db: DbSession):
    try:
        return service.update_payment(db, payment_id, data)
    except PaymentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(payment_id: int, db: DbSession):
    try:
        service.delete_payment(db, payment_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except PaymentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
