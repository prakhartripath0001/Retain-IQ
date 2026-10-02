from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.dependencies import AdminUser, AnalystOrAdmin
from app.db.dependencies import get_db
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from app.services.customer import (
    CustomerNotFoundError,
    CustomerService,
    DuplicateCustomerError,
)

router = APIRouter(prefix="/customers", tags=["Customers"])
service = CustomerService()

DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[CustomerResponse])
def list_customers(
    db: DbSession,
    current_user: AnalystOrAdmin,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    return service.list_customers(db, skip=skip, limit=limit)


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: DbSession,
    current_user: AnalystOrAdmin,
):
    try:
        return service.get_customer(db, customer_id)
    except CustomerNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(
    data: CustomerCreate,
    db: DbSession,
    current_user: AdminUser,
):
    try:
        return service.create_customer(db, data)
    except DuplicateCustomerError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    data: CustomerUpdate,
    db: DbSession,
    current_user: AdminUser,
):
    try:
        return service.update_customer(db, customer_id, data)
    except CustomerNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DuplicateCustomerError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: int,
    db: DbSession,
    current_user: AdminUser,
):
    try:
        service.delete_customer(db, customer_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except CustomerNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc