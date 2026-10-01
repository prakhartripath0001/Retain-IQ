from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate
from app.services.order import CustomerNotFoundError, OrderNotFoundError, OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])
service = OrderService()

DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[OrderResponse])
def list_orders(
    db: DbSession,
    customer_id: int | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    return service.list_orders(
        db, customer_id=customer_id, skip=skip, limit=limit
    )


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: DbSession):
    try:
        return service.get_order(db, order_id)
    except OrderNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order(data: OrderCreate, db: DbSession):
    try:
        return service.create_order(db, data)
    except CustomerNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(order_id: int, data: OrderUpdate, db: DbSession):
    try:
        return service.update_order(db, order_id, data)
    except OrderNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, db: DbSession):
    try:
        service.delete_order(db, order_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except OrderNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
