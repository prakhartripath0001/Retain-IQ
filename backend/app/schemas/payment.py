from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PaymentCreate(BaseModel):
    order_id: int
    amount: float = Field(gt=0)
    payment_method: str = Field(min_length=1, max_length=50)
    status: str = Field(default="pending", max_length=50)
    transaction_id: str | None = Field(default=None, max_length=100)


class PaymentUpdate(BaseModel):
    amount: float | None = Field(default=None, gt=0)
    payment_method: str | None = Field(default=None, min_length=1, max_length=50)
    status: str | None = Field(default=None, max_length=50)
    transaction_id: str | None = Field(default=None, max_length=100)


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    amount: float
    payment_method: str
    status: str
    transaction_id: str | None = None
    created_at: datetime
