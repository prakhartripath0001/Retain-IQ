from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.analytics import (
    ChurnAnalytics,
    CustomerAnalytics,
    OverviewAnalytics,
    RevenueAnalytics,
    SegmentAnalytics,
)
from app.services.analytics import AnalyticsService

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)

service = AnalyticsService()
DbSession = Annotated[Session, Depends(get_db)]


@router.get("/overview", response_model=OverviewAnalytics)
def get_overview(db: DbSession):
    return service.get_overview(db)


@router.get("/revenue", response_model=RevenueAnalytics)
def get_revenue(db: DbSession):
    return service.get_revenue(db)


@router.get("/customers", response_model=CustomerAnalytics)
def get_customers(db: DbSession):
    return service.get_customers(db)


@router.get("/segments", response_model=SegmentAnalytics)
def get_segments(db: DbSession):
    return service.get_segments(db)


@router.get("/churn", response_model=ChurnAnalytics)
def get_churn(db: DbSession):
    return service.get_churn(db)