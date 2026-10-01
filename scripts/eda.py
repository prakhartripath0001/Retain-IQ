
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")  # Save charts without opening a window
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import text

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"

sys.path.insert(0, str(BACKEND_DIR))

from app.db.session import engine

OUTPUT_DIR = PROJECT_ROOT / "reports" / "eda"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")


def load_data():
    """Load the four source tables from MySQL."""
    with engine.connect() as connection:
        customers = pd.read_sql(
            text("SELECT id, name, email, created_at FROM customers"),
            connection,
        )
        orders = pd.read_sql(
            text(
                "SELECT id, customer_id, status, total_amount, created_at "
                "FROM orders"
            ),
            connection,
        )
        items = pd.read_sql(
            text(
                "SELECT id, order_id, product_id, quantity, unit_price "
                "FROM order_items"
            ),
            connection,
        )
        products = pd.read_sql(
            text("SELECT id, name, price, stock_quantity FROM products"),
            connection,
        )

    return customers, orders, items, products


def main():
    customers, orders, items, products = load_data()

    for column in ["total_amount"]:
        if column in orders:
            orders[column] = pd.to_numeric(orders[column], errors="coerce")

    for column in ["quantity", "unit_price"]:
        items[column] = pd.to_numeric(items[column], errors="coerce")

    counts = {
        "customers": len(customers),
        "orders": len(orders),
        "order_items": len(items),
        "products": len(products),
    }

    print("\n========== DATASET OVERVIEW ==========")
    for table, count in counts.items():
        print(f"{table}: {count}")

    valid_orders = orders.loc[
        orders["total_amount"].notna()
        & orders["total_amount"].ge(0)
    ].copy()

    total_revenue = valid_orders["total_amount"].sum()
    order_count = valid_orders["id"].nunique()
    customer_count = customers["id"].nunique()

    buying_customers = (
        valid_orders["customer_id"].nunique()
        if not valid_orders.empty
        else 0
    )

    average_order_value = (
        total_revenue / order_count if order_count else 0
    )

    purchase_frequency = (
        order_count / buying_customers if buying_customers else 0
    )

    print("\n========== KEY METRICS ==========")
    print(f"Registered customers: {customer_count}")
    print(f"Orders with valid amounts: {order_count}")
    print(f"Revenue across these orders: {total_revenue:.2f}")
    print(f"Average order value: {average_order_value:.2f}")
    print(f"Customers with orders: {buying_customers}")
    print(f"Orders per buying customer: {purchase_frequency:.2f}")

    # Customer-level summary
    if not valid_orders.empty:
        customer_summary = (
            valid_orders.groupby("customer_id")
            .agg(
                order_count=("id", "nunique"),
                total_spent=("total_amount", "sum"),
                average_order_value=("total_amount", "mean"),
                last_order_date=("created_at", "max"),
            )
            .reset_index()
        )
    else:
        customer_summary = pd.DataFrame(
            columns=[
                "customer_id",
                "order_count",
                "total_spent",
                "average_order_value",
                "last_order_date",
            ]
        )

    customer_summary = customers[
        ["id", "name", "email"]
    ].merge(
        customer_summary,
        left_on="id",
        right_on="customer_id",
        how="left",
    )

    customer_summary["order_count"] = (
        customer_summary["order_count"].fillna(0).astype(int)
    )

    for column in ["total_spent", "average_order_value"]:
        customer_summary[column] = (
            customer_summary[column].fillna(0)
        )

    customer_summary.to_csv(
        OUTPUT_DIR / "customer_summary.csv", index=False
    )

    # Product performance: units and revenue from order items.
    valid_items = items.loc[
        items["quantity"].notna()
        & items["quantity"].gt(0)
        & items["unit_price"].notna()
        & items["unit_price"].ge(0)
    ].copy()

    valid_items["item_revenue"] = (
        valid_items["quantity"] * valid_items["unit_price"]
    )

    if not valid_items.empty:
        product_summary = (
            valid_items.groupby("product_id")
            .agg(
                units_sold=("quantity", "sum"),
                item_revenue=("item_revenue", "sum"),
            )
            .reset_index()
            .merge(
                products[["id", "name"]],
                left_on="product_id",
                right_on="id",
                how="left",
            )
            .drop(columns=["id"])
            .sort_values("units_sold", ascending=False)
        )
    else:
        product_summary = pd.DataFrame(
            columns=[
                "product_id",
                "name",
                "units_sold",
                "item_revenue",
            ]
        )

    product_summary.to_csv(
        OUTPUT_DIR / "product_performance.csv", index=False
    )

    # Monthly revenue based on orders.created_at.
    valid_orders["created_at"] = pd.to_datetime(
        valid_orders["created_at"], errors="coerce"
    )

    dated_orders = valid_orders.dropna(subset=["created_at"]).copy()

    if not dated_orders.empty:
        dated_orders["month"] = (
            dated_orders["created_at"].dt.to_period("M").astype(str)
        )

        monthly_revenue = (
            dated_orders.groupby("month")["total_amount"]
            .sum()
            .reset_index(name="revenue")
            .sort_values("month")
        )
    else:
        monthly_revenue = pd.DataFrame(
            columns=["month", "revenue"]
        )

    monthly_revenue.to_csv(
        OUTPUT_DIR / "monthly_revenue.csv", index=False
    )

    summary_lines = [
        "RetainIQ - Exploratory Data Analysis",
        "",
        f"Registered customers: {customer_count}",
        f"Orders with valid amounts: {order_count}",
        f"Revenue across these orders: {total_revenue:.2f}",
        f"Average order value: {average_order_value:.2f}",
        f"Customers with orders: {buying_customers}",
        f"Orders per buying customer: {purchase_frequency:.2f}",
        "",
        "Note: revenue includes all statuses until a completed-sale "
        "status policy is defined.",
        "No sales conclusions can be drawn when the orders table is empty.",
    ]

    (OUTPUT_DIR / "eda_summary.txt").write_text(
        "\n".join(summary_lines), encoding="utf-8"
    )

    # Chart 1: customer order-count distribution.
    plt.figure(figsize=(8, 5))
    sns.histplot(customer_summary["order_count"], discrete=True)
    plt.title("Customer Order Distribution")
    plt.xlabel("Number of orders")
    plt.ylabel("Number of customers")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "customer_order_distribution.png")
    plt.close()

    plt.figure(figsize=(9, 5))
    if not monthly_revenue.empty:
        sns.lineplot(
            data=monthly_revenue,
            x="month",
            y="revenue",
            marker="o",
        )
        plt.xticks(rotation=45)
    else:
        plt.text(
            0.5, 0.5, "No order data available yet",
            ha="center", va="center",
            transform=plt.gca().transAxes,
        )
    plt.title("Monthly Revenue Trend")
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "monthly_revenue.png")
    plt.close()

    plt.figure(figsize=(9, 5))
    if not product_summary.empty:
        top_products = product_summary.head(10)
        sns.barplot(
            data=top_products,
            x="units_sold",
            y="name",
        )
    else:
        plt.text(
            0.5, 0.5, "No product sales available yet",
            ha="center", va="center",
            transform=plt.gca().transAxes,
        )
    plt.title("Top Products by Units Sold")
    plt.xlabel("Units sold")
    plt.ylabel("Product")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "product_performance.png")
    plt.close()

    amounts = valid_orders["total_amount"].dropna().to_numpy(
        dtype=float
    )
    median_order_value = float(np.median(amounts)) if len(amounts) else 0

    print(f"Median order value: {median_order_value:.2f}")
    print(f"\nEDA files saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()