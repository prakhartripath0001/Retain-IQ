from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.prediction import ChurnPredictionResponse
from app.services.prediction import CustomerNotFoundError, PredictionService

router = APIRouter(prefix="/predictions", tags=["Predictions"])
service = PredictionService()

DbSession = Annotated[Session, Depends(get_db)]


@router.post("/churn/{customer_id}", response_model=ChurnPredictionResponse)
def predict_churn(customer_id: int, db: DbSession):
    try:
        return service.predict_churn(db, customer_id)
    except CustomerNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
