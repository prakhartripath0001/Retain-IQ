from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, default=1)
    unit_price: float = Field(gt=0)


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price: float


class OrderCreate(BaseModel):
    customer_id: int
    status: str = Field(default="pending", max_length=50)
    total_amount: float = Field(gt=0)
    items: list[OrderItemCreate] = []


class OrderUpdate(BaseModel):
    status: str | None = Field(default=None, max_length=50)
    total_amount: float | None = Field(default=None, gt=0)


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    status: str
    total_amount: float
    created_at: datetime
    items: list[OrderItemResponse] = []
