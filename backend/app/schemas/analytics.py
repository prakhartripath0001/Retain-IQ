from pydantic import BaseModel, ConfigDict


class OverviewAnalytics(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_revenue: float
    customers: int
    orders: int
    churn_rate: float
    average_order_value: float


class MonthlyRevenueItem(BaseModel):
    month: str
    revenue: float


class RevenueAnalytics(BaseModel):
    total_revenue: float
    average_order_value: float
    monthly_revenue: list[MonthlyRevenueItem]


class CustomerAnalytics(BaseModel):
    total_customers: int
    buying_customers: int
    avg_orders_per_customer: float
    avg_customer_spend: float


class SegmentProfileItem(BaseModel):
    segment: str
    customer_count: int
    avg_recency_days: float | None = None
    avg_frequency: float | None = None
    avg_monetary: float | None = None


class SegmentAnalytics(BaseModel):
    total_segments: int
    segments: list[SegmentProfileItem]


class ChurnAnalytics(BaseModel):
    total_eligible_customers: int
    churned_customers: int
    retained_customers: int
    churn_rate: float
    observation_date: str | None = None
