
from pathlib import Path
import sys
import math

import numpy as np
import pandas as pd
from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"

sys.path.insert(0, str(BACKEND_DIR))

from app.db.session import engine  

OUTPUT_DIR = PROJECT_ROOT / "reports" / "rfm"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "customer_rfm.csv"


def load_data():
    """Load customers and orders from MySQL."""
    with engine.connect() as connection:
        customers = pd.read_sql(
            text("SELECT id, name, email FROM customers"),
            connection,
        )

        orders = pd.read_sql(
            text("""
                SELECT id, customer_id, total_amount, created_at, status
                FROM orders
            """),
            connection,
        )

    return customers, orders


def assign_score(series, higher_is_better=True):
    """
    Assign scores from 1 to 5 using relative ranks.
    Works with small datasets without qcut duplicate-bin errors.
    """
    valid = series.notna()
    scores = pd.Series(pd.NA, index=series.index, dtype="Int64")

    if valid.sum() == 0:
        return scores

    ranks = series.loc[valid].rank(
        method="first",
        ascending=not higher_is_better,
        pct=True,
    )

    scores.loc[valid] = np.ceil(ranks * 5).clip(1, 5).astype(int)
    return scores


def main():
    customers, orders = load_data()

    orders["total_amount"] = pd.to_numeric(
        orders["total_amount"], errors="coerce"
    )
    orders["created_at"] = pd.to_datetime(
        orders["created_at"], errors="coerce"
    )

    eligible = orders.loc[
        orders["customer_id"].notna()
        & orders["created_at"].notna()
        & orders["total_amount"].notna()
        & orders["total_amount"].ge(0)
    ].copy()

    eligible = eligible[
        eligible["customer_id"].isin(customers["id"])
    ]

    eligible = eligible.drop_duplicates(
        subset=["id"], keep="first"
    )

    if not eligible.empty:
        reference_date = (
            eligible["created_at"].max().normalize()
            + pd.Timedelta(days=1)
        )
    else:
        reference_date = pd.Timestamp.now().normalize()

    if not eligible.empty:
        rfm = (
            eligible.groupby("customer_id")
            .agg(
                last_purchase=("created_at", "max"),
                frequency=("id", "nunique"),
                monetary=("total_amount", "sum"),
            )
            .reset_index()
        )

        rfm["recency_days"] = (
            reference_date - rfm["last_purchase"].dt.normalize()
        ).dt.days

        rfm = rfm.drop(columns=["last_purchase"])
    else:
        rfm = pd.DataFrame(
            columns=[
                "customer_id",
                "frequency",
                "monetary",
                "recency_days",
            ]
        )

    result = customers.merge(
        rfm,
        left_on="id",
        right_on="customer_id",
        how="left",
    )

    result["frequency"] = result["frequency"].fillna(0).astype(int)
    result["monetary"] = result["monetary"].fillna(0.0)

    has_purchases = result["frequency"] > 0

    result["R_score"] = pd.Series(
        pd.NA, index=result.index, dtype="Int64"
    )
    result["F_score"] = pd.Series(
        pd.NA, index=result.index, dtype="Int64"
    )
    result["M_score"] = pd.Series(
        pd.NA, index=result.index, dtype="Int64"
    )

    result.loc[has_purchases, "R_score"] = assign_score(
        result.loc[has_purchases, "recency_days"],
        higher_is_better=False,
    )

    result.loc[has_purchases, "F_score"] = assign_score(
        result.loc[has_purchases, "frequency"],
        higher_is_better=True,
    )

    result.loc[has_purchases, "M_score"] = assign_score(
        result.loc[has_purchases, "monetary"],
        higher_is_better=True,
    )

    result["RFM_score"] = (
        result["R_score"].astype("string")
        + result["F_score"].astype("string")
        + result["M_score"].astype("string")
    )

    result["segment"] = np.where(
        has_purchases,
        "Customer with purchases",
        "No purchases",
    )

    columns = [
        "id",
        "name",
        "email",
        "recency_days",
        "frequency",
        "monetary",
        "R_score",
        "F_score",
        "M_score",
        "RFM_score",
        "segment",
    ]

    result[columns].to_csv(OUTPUT_FILE, index=False)

    print("\n========== RETAINIQ RFM ANALYSIS ==========")
    print(f"Customers analyzed: {len(result)}")
    print(f"Eligible orders: {len(eligible)}")
    print(f"Customers with purchases: {int(has_purchases.sum())}")
    print(f"Customers without purchases: {int((~has_purchases).sum())}")
    print(f"Reference date: {reference_date.date()}")
    print(f"Output file: {OUTPUT_FILE}")

    print("\nRFM results:")
    print(result[columns].to_string(index=False))


if __name__ == "__main__":
    main()