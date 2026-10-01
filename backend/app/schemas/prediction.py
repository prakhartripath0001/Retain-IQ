from pydantic import BaseModel, Field


class ChurnPredictionResponse(BaseModel):
    customer_id: int
    probability: float = Field(ge=0.0, le=1.0)
    risk_level: str
    factors: list[str]
