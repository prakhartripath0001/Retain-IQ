from pathlib import Path

import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.order import Order
from app.schemas.analytics import (
    ChurnAnalytics,
    CustomerAnalytics,
    MonthlyRevenueItem,
    OverviewAnalytics,
    RevenueAnalytics,
    SegmentAnalytics,
    SegmentProfileItem,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
REPORTS_DIR = PROJECT_ROOT / "reports"


class AnalyticsService:
    def get_overview(self, db: Session) -> OverviewAnalytics:
        customer_count = db.scalar(select(func.count(Customer.id))) or 0
        order_count = db.scalar(select(func.count(Order.id))) or 0
        total_revenue = db.scalar(select(func.sum(Order.total_amount))) or 0.0

        avg_aov = float(total_revenue / order_count) if order_count > 0 else 0.0

        churn_info = self.get_churn(db)
        churn_rate = churn_info.churn_rate

        return OverviewAnalytics(
            total_revenue=round(float(total_revenue), 2),
            customers=customer_count,
            orders=order_count,
            churn_rate=round(churn_rate, 4),
            average_order_value=round(avg_aov, 2),
        )

    def get_revenue(self, db: Session) -> RevenueAnalytics:
        order_count = db.scalar(select(func.count(Order.id))) or 0
        total_revenue = db.scalar(select(func.sum(Order.total_amount))) or 0.0
        avg_aov = float(total_revenue / order_count) if order_count > 0 else 0.0

        monthly_csv = REPORTS_DIR / "eda" / "monthly_revenue.csv"
        monthly_items: list[MonthlyRevenueItem] = []

        if monthly_csv.exists():
            df = pd.read_csv(monthly_csv)
            for _, row in df.iterrows():
                monthly_items.append(
                    MonthlyRevenueItem(
                        month=str(row["month"]),
                        revenue=round(float(row["revenue"]), 2),
                    )
                )

        return RevenueAnalytics(
            total_revenue=round(float(total_revenue), 2),
            average_order_value=round(avg_aov, 2),
            monthly_revenue=monthly_items,
        )

    def get_customers(self, db: Session) -> CustomerAnalytics:
        customer_count = db.scalar(select(func.count(Customer.id))) or 0
        buying_customers = (
            db.scalar(select(func.count(func.distinct(Order.customer_id)))) or 0
        )
        order_count = db.scalar(select(func.count(Order.id))) or 0
        total_revenue = db.scalar(select(func.sum(Order.total_amount))) or 0.0

        avg_orders = (
            float(order_count / buying_customers) if buying_customers > 0 else 0.0
        )
        avg_spend = (
            float(total_revenue / buying_customers) if buying_customers > 0 else 0.0
        )

        return CustomerAnalytics(
            total_customers=customer_count,
            buying_customers=buying_customers,
            avg_orders_per_customer=round(avg_orders, 2),
            avg_customer_spend=round(avg_spend, 2),
        )

    def get_segments(self, db: Session) -> SegmentAnalytics:
        profile_csv = REPORTS_DIR / "segmentation" / "cluster_profiles.csv"
        segment_items: list[SegmentProfileItem] = []

        if profile_csv.exists():
            df = pd.read_csv(profile_csv)
            for _, row in df.iterrows():
                segment_items.append(
                    SegmentProfileItem(
                        segment=str(row.get("segment", "Unknown")),
                        customer_count=int(row.get("customer_count", 0)),
                        avg_recency_days=round(float(row.get("recency_days", 0)), 2)
                        if "recency_days" in row
                        else None,
                        avg_frequency=round(float(row.get("frequency", 0)), 2)
                        if "frequency" in row
                        else None,
                        avg_monetary=round(float(row.get("monetary", 0)), 2)
                        if "monetary" in row
                        else None,
                    )
                )

        return SegmentAnalytics(
            total_segments=len(segment_items),
            segments=segment_items,
        )

    def get_churn(self, db: Session) -> ChurnAnalytics:
        churn_csv = REPORTS_DIR / "churn" / "churn_labels.csv"

        if churn_csv.exists():
            df = pd.read_csv(churn_csv)
            total = len(df)
            churned = int((df["churn"] == 1).sum())
            retained = total - churned
            rate = float(churned / total) if total > 0 else 0.0
            obs_date = (
                str(df["observation_date"].iloc[0])
                if "observation_date" in df.columns and not df.empty
                else None
            )

            return ChurnAnalytics(
                total_eligible_customers=total,
                churned_customers=churned,
                retained_customers=retained,
                churn_rate=round(rate, 4),
                observation_date=obs_date,
            )

        return ChurnAnalytics(
            total_eligible_customers=0,
            churned_customers=0,
            retained_customers=0,
            churn_rate=0.0,
            observation_date=None,
        )
