"""
scripts/seed_sample_data.py
----------------------------
Seeds MySQL with realistic sample data for EDA:
  - 50 customers
  - 10 products
  - 200 orders (spread across 12 months)
  - 400+ order_items

Run from the project root with the backend venv active:
    python scripts/seed_sample_data.py
"""

from __future__ import annotations

import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.db.session import engine  # noqa: E402

random.seed(42)

FIRST_NAMES = [
    "Alice", "Bob", "Charlie", "Diana", "Evan", "Fiona", "George", "Hannah",
    "Ian", "Julia", "Kevin", "Laura", "Mike", "Nina", "Oscar", "Priya",
    "Quinn", "Rachel", "Sam", "Tara", "Uma", "Victor", "Wendy", "Xavier",
    "Yara", "Zoe", "Aaron", "Beth", "Carl", "Donna", "Eric", "Grace",
    "Henry", "Iris", "Jack", "Kara", "Leo", "Mia", "Noah", "Olivia",
    "Paul", "Queen", "Ryan", "Sara", "Tom", "Uma", "Vince", "Will",
    "Xena", "Yvonne",
]

PRODUCTS = [
    ("Wireless Headphones",  79.99),
    ("Running Shoes",        120.00),
    ("Coffee Maker",         59.99),
    ("Yoga Mat",             35.00),
    ("Laptop Stand",         45.00),
    ("Mechanical Keyboard",  99.99),
    ("Desk Lamp",            29.99),
    ("Water Bottle",         18.00),
    ("Backpack",             65.00),
    ("Smart Watch",         199.99),
]

STATUSES = ["completed", "completed", "completed", "shipped", "pending", "cancelled"]


def random_date(start: datetime, days: int) -> datetime:
    return start + timedelta(days=random.randint(0, days), hours=random.randint(0, 23))


def main() -> None:
    start_date = datetime(2024, 1, 1)
    date_range_days = 550  # spans Jan 2024 → Jun 2025

    with engine.begin() as conn:
        # ── Clear existing data (child → parent order) ──────────────────
        conn.execute(text("DELETE FROM order_items"))
        conn.execute(text("DELETE FROM orders"))
        conn.execute(text("DELETE FROM products"))
        conn.execute(text("DELETE FROM customers"))
        print("Cleared existing data.")

        # ── Customers ────────────────────────────────────────────────────
        customers = []
        for i, name in enumerate(FIRST_NAMES, start=1):
            email = f"{name.lower()}.{i}@example.com"
            phone = f"555-{i:04d}"
            created = random_date(start_date, date_range_days)
            conn.execute(
                text(
                    "INSERT INTO customers (id, name, email, phone, created_at) "
                    "VALUES (:id, :name, :email, :phone, :created_at)"
                ),
                {"id": i, "name": name, "email": email, "phone": phone, "created_at": created},
            )
            customers.append({"id": i, "created_at": created})
        print(f"Inserted {len(customers)} customers.")

        # ── Products ─────────────────────────────────────────────────────
        products = []
        for i, (name, price) in enumerate(PRODUCTS, start=1):
            stock = random.randint(20, 500)
            conn.execute(
                text(
                    "INSERT INTO products (id, name, price, stock_quantity) "
                    "VALUES (:id, :name, :price, :stock_quantity)"
                ),
                {"id": i, "name": name, "price": price, "stock_quantity": stock},
            )
            products.append({"id": i, "price": price})
        print(f"Inserted {len(products)} products.")

        # ── Orders + Order Items ─────────────────────────────────────────
        order_id = 1
        item_id = 1
        total_orders = 0
        total_items = 0

        for customer in customers:
            # Each customer places between 1 and 8 orders
            num_orders = random.randint(1, 8)
            for _ in range(num_orders):
                status = random.choice(STATUSES)
                order_date = random_date(start_date, date_range_days)

                # Each order has 1–4 items
                num_items = random.randint(1, 4)
                order_total = 0.0
                item_rows = []

                for _ in range(num_items):
                    product = random.choice(products)
                    qty = random.randint(1, 5)
                    unit_price = round(product["price"] * random.uniform(0.85, 1.10), 2)
                    order_total += qty * unit_price
                    item_rows.append({
                        "id": item_id,
                        "order_id": order_id,
                        "product_id": product["id"],
                        "quantity": qty,
                        "unit_price": unit_price,
                    })
                    item_id += 1

                order_total = round(order_total, 2)

                conn.execute(
                    text(
                        "INSERT INTO orders (id, customer_id, status, total_amount, created_at) "
                        "VALUES (:id, :customer_id, :status, :total_amount, :created_at)"
                    ),
                    {
                        "id": order_id,
                        "customer_id": customer["id"],
                        "status": status,
                        "total_amount": order_total,
                        "created_at": order_date,
                    },
                )

                for item in item_rows:
                    conn.execute(
                        text(
                            "INSERT INTO order_items (id, order_id, product_id, quantity, unit_price) "
                            "VALUES (:id, :order_id, :product_id, :quantity, :unit_price)"
                        ),
                        item,
                    )

                order_id += 1
                total_orders += 1
                total_items += len(item_rows)

        print(f"Inserted {total_orders} orders.")
        print(f"Inserted {total_items} order items.")

    print("\n✅ Sample data seeded successfully!")
    print(f"   Customers  : {len(customers)}")
    print(f"   Products   : {len(products)}")
    print(f"   Orders     : {total_orders}")
    print(f"   Order items: {total_items}")


if __name__ == "__main__":
    main()
