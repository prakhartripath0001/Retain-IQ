
import os
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.db.session import engine  

OUTPUT_DIR = PROJECT_ROOT / "reports" / "churn"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "churn_labels.csv"

# Required configuration: provide both dates in YYYY-MM-DD format.
SNAPSHOT_DATE = os.getenv("CHURN_SNAPSHOT_DATE")
DATA_THROUGH_DATE = os.getenv("CHURN_DATA_THROUGH_DATE")

HORIZON_DAYS = 90


PURCHASE_STATUSES = {
    "completed",
    "paid",
    "delivered",
    "shipped",
}


def load_data():
    with engine.connect() as connection:
        customers = pd.read_sql(
            text("""
                SELECT id, name, email
                FROM customers
            """),
            connection,
        )

        orders = pd.read_sql(
            text("""
                SELECT id, customer_id, created_at, status
                FROM orders
            """),
            connection,
        )

    return customers, orders


def generate_labels(customers, orders, snapshot_date, data_through_date):
    snapshot = pd.Timestamp(snapshot_date).normalize()
    data_through = pd.Timestamp(data_through_date).normalize()
    horizon_end = snapshot + pd.Timedelta(days=HORIZON_DAYS)

    if data_through < horizon_end:
        raise ValueError(
            f"Insufficient follow-up data. The observation date is "
            f"{snapshot.date()}, so data must be complete through at least "
            f"{horizon_end.date()}. You declared complete data through "
            f"{data_through.date()}."
        )

    customers = customers.drop_duplicates(subset=["id"]).copy()
    orders = orders.copy()

    orders["created_at"] = pd.to_datetime(
        orders["created_at"], errors="coerce"
    )
    orders["status_normalized"] = (
        orders["status"].astype("string").str.strip().str.lower()
    )

    valid_orders = orders.loc[
        orders["created_at"].notna()
        & orders["customer_id"].isin(customers["id"])
        & orders["status_normalized"].isin(PURCHASE_STATUSES)
    ].drop_duplicates(subset=["id"])

    historical = valid_orders.loc[
        valid_orders["created_at"] <= snapshot
    ]

    eligible_customers = historical["customer_id"].unique()


    future = valid_orders.loc[
        (valid_orders["created_at"] > snapshot)
        & (valid_orders["created_at"] <= horizon_end)
    ]

    future_customer_ids = set(future["customer_id"].unique())

    historical_features = (
        historical.groupby("customer_id")
        .agg(
            last_purchase_date=("created_at", "max"),
            historical_order_count=("id", "nunique"),
        )
        .reset_index()
    )

    result = customers.loc[
        customers["id"].isin(eligible_customers)
    ].merge(
        historical_features,
        left_on="id",
        right_on="customer_id",
        how="left",
    ).drop(columns=["customer_id"])

    result["recency_days_at_snapshot"] = (
        snapshot - result["last_purchase_date"].dt.normalize()
    ).dt.days

    result["churn"] = (
        ~result["id"].isin(future_customer_ids)
    ).astype("int8")

    result["observation_date"] = snapshot.date().isoformat()
    result["label_window_end"] = horizon_end.date().isoformat()
    result["data_through_date"] = data_through.date().isoformat()
    result["label_definition"] = "No qualifying purchase in next 90 days"

    return result


def main():
    if not SNAPSHOT_DATE or not DATA_THROUGH_DATE:
        raise ValueError(
            "Set CHURN_SNAPSHOT_DATE and CHURN_DATA_THROUGH_DATE first. "
            "Use YYYY-MM-DD format and ensure data-through date is at least "
            "90 days after the observation date."
        )

    customers, orders = load_data()

    if customers.empty:
        raise ValueError("The customers table is empty.")

    result = generate_labels(
        customers,
        orders,
        SNAPSHOT_DATE,
        DATA_THROUGH_DATE,
    )

    result.to_csv(OUTPUT_FILE, index=False)

    print("\n========== RETAINIQ CHURN LABELS ==========")
    print(f"Observation date: {SNAPSHOT_DATE}")
    print(f"Data complete through: {DATA_THROUGH_DATE}")
    print(f"Label window: 90 days")
    print(f"Eligible customers: {len(result)}")

    if result.empty:
        print(
            "No customers had a qualifying purchase by the observation date."
        )
    else:
        print("\nLabel counts:")
        print(
            result["churn"]
            .map({0: "Not churned (0)", 1: "Churned (1)"})
            .value_counts()
            .to_string()
        )

        print("\nSample labels:")
        print(
            result[
                [
                    "id",
                    "name",
                    "recency_days_at_snapshot",
                    "historical_order_count",
                    "churn",
                ]
            ].head(10).to_string(index=False)
        )

    print(f"\nSaved labels to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()