
import os
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import inspect, text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.db.session import engine  # noqa: E402

OUTPUT_DIR = PROJECT_ROOT / "reports" / "features"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "customer_features.csv"

SNAPSHOT_DATE = os.getenv("FEATURE_SNAPSHOT_DATE", date.today().isoformat())

PURCHASE_STATUSES = {"completed", "paid", "delivered", "shipped"}


def load_tables():
    """Load available tables and inspect their columns."""
    inspector = inspect(engine)
    available_tables = set(inspector.get_table_names())
    required_tables = {"customers", "orders"}

    missing = required_tables - available_tables
    if missing:
        raise ValueError(f"Missing required database tables: {missing}")

    tables = {}

    with engine.connect() as connection:
        for table_name in [
            "customers",
            "orders",
            "order_items",
            "reviews",
        ]:
            if table_name in available_tables:
                tables[table_name] = pd.read_sql(
                    text(f"SELECT * FROM `{table_name}`"),
                    connection,
                )

    return tables


def find_column(df, candidates):
    """Return the first matching column name, ignoring case."""
    lookup = {column.lower(): column for column in df.columns}
    for candidate in candidates:
        if candidate.lower() in lookup:
            return lookup[candidate.lower()]
    return None


def to_number(series):
    return pd.to_numeric(series, errors="coerce")


def build_features(tables, snapshot_date):
    customers = tables["customers"].copy()
    orders = tables["orders"].copy()

    required_customer_cols = {"id", "name", "email"}
    if not required_customer_cols.issubset(customers.columns):
        raise ValueError(
            "The customers table must contain id, name and email."
        )

    required_order_cols = {
        "id", "customer_id", "total_amount", "created_at"
    }
    if not required_order_cols.issubset(orders.columns):
        raise ValueError(
            "The orders table must contain id, customer_id, "
            "total_amount and created_at."
        )

    snapshot = pd.Timestamp(snapshot_date).normalize()
    cutoff = snapshot + pd.Timedelta(days=1)

    customers = customers.drop_duplicates(subset=["id"]).copy()

    orders["created_at"] = pd.to_datetime(
        orders["created_at"], errors="coerce"
    )
    orders["total_amount"] = to_number(orders["total_amount"])

    if "status" in orders.columns:
        status = orders["status"].astype("string").str.strip().str.lower()
        orders = orders.loc[status.isin(PURCHASE_STATUSES)].copy()

    orders = orders.loc[
        orders["created_at"].notna()
        & orders["total_amount"].notna()
        & orders["customer_id"].isin(customers["id"])
        & orders["created_at"].lt(cutoff)
        & orders["total_amount"].ge(0)
    ].drop_duplicates(subset=["id"])


    last_30_start = cutoff - pd.Timedelta(days=30)
    last_90_start = cutoff - pd.Timedelta(days=90)

    orders_30 = orders.loc[orders["created_at"].ge(last_30_start)]
    orders_90 = orders.loc[orders["created_at"].ge(last_90_start)]

    all_stats = (
        orders.groupby("customer_id")
        .agg(
            last_order_date=("created_at", "max"),
            total_orders=("id", "nunique"),
            total_spending=("total_amount", "sum"),
        )
        .reset_index()
    )

    stats_30 = (
        orders_30.groupby("customer_id")
        .agg(
            orders_last_30_days=("id", "nunique"),
            spending_last_30_days=("total_amount", "sum"),
        )
        .reset_index()
    )

    stats_90 = (
        orders_90.groupby("customer_id")
        .agg(
            orders_last_90_days=("id", "nunique"),
            spending_last_90_days=("total_amount", "sum"),
        )
        .reset_index()
    )

    features = customers[["id", "name", "email"]].copy()
    features = features.merge(
        all_stats, left_on="id", right_on="customer_id", how="left"
    ).drop(columns=["customer_id"])
    features = features.merge(
        stats_30, left_on="id", right_on="customer_id", how="left"
    ).drop(columns=["customer_id"])
    features = features.merge(
        stats_90, left_on="id", right_on="customer_id", how="left"
    ).drop(columns=["customer_id"])

    features["days_since_last_order"] = (
        cutoff - features["last_order_date"]
    ).dt.days

    count_cols = [
        "total_orders",
        "orders_last_30_days",
        "orders_last_90_days",
    ]
    spending_cols = [
        "total_spending",
        "spending_last_30_days",
        "spending_last_90_days",
    ]

    for column in count_cols:
        features[column] = features[column].fillna(0).astype(int)

    for column in spending_cols:
        features[column] = features[column].fillna(0.0)

    features["average_order_value"] = (
        features["total_spending"]
        / features["total_orders"].replace(0, np.nan)
    )

    features = features.drop(columns=["last_order_date"])

    discount_column = find_column(
        orders,
        [
            "discount_used", "discount_amount", "discount",
            "discount_code", "coupon_code", "coupon_id",
        ],
    )

    if discount_column is not None:
        values = orders[discount_column]

        if discount_column.lower() in {
            "discount_used", "discount_code", "coupon_code", "coupon_id"
        }:
            used = (
                values.notna()
                & values.astype("string").str.strip().ne("")
                & values.astype("string").str.lower().ne("false")
                & values.astype("string").str.lower().ne("none")
                & values.astype("string").ne("0")
            )
        else:
            used = to_number(values).fillna(0).gt(0)

        discount_by_customer = (
            orders.assign(_discount_used=used.astype(int))
            .groupby("customer_id")["_discount_used"]
            .mean()
        )

        features["discount_usage"] = features["id"].map(
            discount_by_customer
        )
    else:
        features["discount_usage"] = np.nan

    reviews = tables.get("reviews", pd.DataFrame())
    rating_col = find_column(
        reviews,
        ["rating", "review_score", "score", "stars"],
    )
    review_customer_col = find_column(reviews, ["customer_id"])
    review_date_col = find_column(
        reviews, ["created_at", "review_date", "date"]
    )

    if not reviews.empty and rating_col and review_customer_col:
        reviews = reviews.copy()
        reviews[rating_col] = to_number(reviews[rating_col])

        if review_date_col:
            reviews[review_date_col] = pd.to_datetime(
                reviews[review_date_col], errors="coerce"
            )
            reviews = reviews.loc[
                reviews[review_date_col].notna()
                & reviews[review_date_col].lt(cutoff)
            ]

        review_means = (
            reviews.dropna(subset=[rating_col])
            .groupby(review_customer_col)[rating_col]
            .mean()
        )
        features["average_review_score"] = features["id"].map(
            review_means
        )
    else:
        features["average_review_score"] = np.nan

    items = tables.get("order_items", pd.DataFrame())
    quantity_col = find_column(items, ["quantity"])
    returned_qty_col = find_column(
        items, ["returned_quantity", "return_quantity"]
    )
    returned_flag_col = find_column(
        items, ["is_returned", "returned", "return_status"]
    )
    item_order_col = find_column(items, ["order_id"])

    features["return_rate"] = np.nan

    if (
        not items.empty
        and quantity_col
        and item_order_col
        and (returned_qty_col or returned_flag_col)
    ):
        items = items.copy()
        items[quantity_col] = to_number(items[quantity_col]).fillna(0)

        eligible_order_ids = set(orders["id"])
        items = items.loc[
            items[item_order_col].isin(eligible_order_ids)
        ].copy()

        if returned_qty_col:
            items["_returned_units"] = (
                to_number(items[returned_qty_col]).fillna(0)
            )
        else:
            flag = (
                items[returned_flag_col]
                .astype("string")
                .str.strip()
                .str.lower()
            )
            is_returned = flag.isin(
                {"true", "1", "yes", "returned", "refunded"}
            )
            items["_returned_units"] = np.where(
                is_returned, items[quantity_col], 0
            )

        order_to_customer = orders.set_index("id")["customer_id"]
        items["_customer_id"] = items[item_order_col].map(
            order_to_customer
        )

        returned = items.groupby("_customer_id")["_returned_units"].sum()
        purchased_units = items.groupby("_customer_id")[quantity_col].sum()

        rate = returned.div(purchased_units.replace(0, np.nan))
        features["return_rate"] = features["id"].map(rate).clip(0, 1)

    features["snapshot_date"] = snapshot.date().isoformat()

    columns = [
        "id",
        "name",
        "email",
        "snapshot_date",
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

    return features[columns]


def main():
    tables = load_tables()
    features = build_features(tables, SNAPSHOT_DATE)
    features.to_csv(OUTPUT_FILE, index=False)

    print("\n========== RETAINIQ FEATURE ENGINEERING ==========")
    print(f"Snapshot date: {SNAPSHOT_DATE}")
    print(f"Customers: {len(features)}")
    print(f"Feature columns: {len(features.columns) - 4}")
    print("\nMissing values by feature:")
    print(features.isna().sum().to_string())
    print(f"\nSaved dataset: {OUTPUT_FILE}")
    print("\nSample rows:")
    print(features.head(5).to_string(index=False))


if __name__ == "__main__":
    main()