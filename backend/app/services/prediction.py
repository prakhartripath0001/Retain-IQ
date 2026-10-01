from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.order import Order
from app.schemas.prediction import ChurnPredictionResponse

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_FILE = PROJECT_ROOT / "reports" / "models" / "churn_model.joblib"

FEATURE_COLUMNS = [
    "days_since_last_order",
    "total_orders",
    "total_spending",
    "average_order_value",
    "orders_last_30_days",
    "orders_last_90_days",
    "spending_last_30_days",
    "spending_last_90_days",
    "return_rate",
    "average_review_score",
    "discount_usage",
]


class CustomerNotFoundError(Exception):
    pass


class PredictionService:
    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            if MODEL_FILE.exists():
                self._model = joblib.load(MODEL_FILE)
            else:
                self._model = None
        return self._model

    def predict_churn(self, db: Session, customer_id: int) -> ChurnPredictionResponse:
        customer = db.get(Customer, customer_id)
        if customer is None:
            raise CustomerNotFoundError(f"Customer {customer_id} was not found")

        features_df = self._extract_customer_features(db, customer_id)

        if self.model is not None:
            prob = float(self.model.predict_proba(features_df)[0][1])
        else:
            # Fallback heuristic if model file is not available
            days = features_df["days_since_last_order"].iloc[0]
            orders_90 = features_df["orders_last_90_days"].iloc[0]
            if pd.isna(days) or days > 180:
                prob = 0.85
            elif days > 90 or orders_90 == 0:
                prob = 0.65
            else:
                prob = 0.25

        prob = max(0.0, min(1.0, prob))

        if prob >= 0.70:
            risk_level = "HIGH"
        elif prob >= 0.40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        factors = self._explain_factors(features_df, prob)

        return ChurnPredictionResponse(
            customer_id=customer_id,
            probability=round(prob, 2),
            risk_level=risk_level,
            factors=factors,
        )

    def _extract_customer_features(self, db: Session, customer_id: int) -> pd.DataFrame:
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        orders = list(
            db.scalars(
                select(Order)
                .where(Order.customer_id == customer_id)
                .order_by(Order.created_at.desc())
            ).all()
        )

        total_orders = len(orders)
        total_spending = sum(o.total_amount for o in orders)
        avg_aov = total_spending / total_orders if total_orders > 0 else 0.0

        if total_orders > 0:
            last_order_date = orders[0].created_at
            days_since_last = (now - last_order_date).days
        else:
            days_since_last = None

        orders_30 = sum(1 for o in orders if (now - o.created_at).days <= 30)
        orders_90 = sum(1 for o in orders if (now - o.created_at).days <= 90)

        spending_30 = sum(
            o.total_amount for o in orders if (now - o.created_at).days <= 30
        )
        spending_90 = sum(
            o.total_amount for o in orders if (now - o.created_at).days <= 90
        )

        feature_dict = {
            "days_since_last_order": [days_since_last],
            "total_orders": [total_orders],
            "total_spending": [total_spending],
            "average_order_value": [avg_aov],
            "orders_last_30_days": [orders_30],
            "orders_last_90_days": [orders_90],
            "spending_last_30_days": [spending_30],
            "spending_last_90_days": [spending_90],
            "return_rate": [None],
            "average_review_score": [None],
            "discount_usage": [None],
        }

        return pd.DataFrame(feature_dict, columns=FEATURE_COLUMNS)

    def _explain_factors(self, df: pd.DataFrame, probability: float) -> list[str]:
        factors = []
        row = df.iloc[0]

        days = row["days_since_last_order"]
        orders_30 = row["orders_last_30_days"]
        orders_90 = row["orders_last_90_days"]
        spending_90 = row["spending_last_90_days"]
        total_orders = row["total_orders"]

        if pd.isna(days) or days > 60:
            factors.append("Long time since last purchase")

        if orders_90 <= 1:
            factors.append("Reduced purchase frequency")

        if orders_30 == 0:
            factors.append("No activity in the last 30 days")

        if spending_90 == 0:
            factors.append("Zero spending in recent months")

        if total_orders < 3:
            factors.append("Low overall order history")

        if not factors and probability < 0.40:
            factors.append("Frequent recent purchases")
            factors.append("Consistent spending pattern")

        return factors[:3]
