from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import text

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.db.session import engine 

SOURCE_FILE = PROJECT_ROOT / "data" / "raw" / "orders.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
CLEANED_FILE = PROCESSED_DIR / "cleaned_orders.csv"
REJECTED_FILE = PROCESSED_DIR / "rejected_orders.csv"

REQUIRED_COLUMNS = {"id", "customer_id", "status", "total_amount", "created_at"}
NUMERIC_COLUMNS = ["id", "customer_id", "total_amount"]
DATE_COLUMNS = ["created_at"]
DEDUP_KEY = "id"  


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    if not SOURCE_FILE.exists():
        raise FileNotFoundError(f"CSV not found: {SOURCE_FILE}")

    df = pd.read_csv(SOURCE_FILE, dtype=str, keep_default_na=False)
    total_read = len(df)
    print(f"[1/6] Read {total_read} rows from {SOURCE_FILE.name}")

    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    if missing_cols:
        raise ValueError(f"CSV is missing required columns: {sorted(missing_cols)}")
    print(f"[2/6] Schema OK — all required columns present: {sorted(REQUIRED_COLUMNS)}")

    # ------------------------------------------------------------------
    # 3. Type coercion
    # ------------------------------------------------------------------
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in DATE_COLUMNS:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    if "status" in df.columns:
        df["status"] = df["status"].str.strip().str.lower()

    print("[3/6] Type coercion applied (numeric + datetime)")

    valid_rows: list[dict] = []
    rejected_rows: list[dict] = []

    seen_ids: set = set()

    for _, row in df.iterrows():
        reason: str | None = None

        if pd.isna(row["id"]):
            reason = "Missing order id"
        elif pd.isna(row["customer_id"]):
            reason = "Missing customer_id"
        elif not str(row.get("status", "")).strip():
            reason = "Missing status"
        elif pd.isna(row["total_amount"]):
            reason = "Missing or non-numeric total_amount"
        elif pd.isna(row["created_at"]):
            reason = "Missing or unparseable created_at"

        elif row["total_amount"] <= 0:
            reason = f"Invalid total_amount: {row['total_amount']} (must be > 0)"

        # 4c. Duplicate order id within this CSV
        elif int(row["id"]) in seen_ids:
            reason = f"Duplicate order id: {int(row['id'])}"

        if reason:
            rejected_rows.append({**row.to_dict(), "rejection_reason": reason})
        else:
            seen_ids.add(int(row["id"]))
            valid_rows.append(row.to_dict())

    print(
        f"[4/6] Validation complete — "
        f"{len(valid_rows)} valid, {len(rejected_rows)} rejected so far"
    )

    if valid_rows:
        valid_df = pd.DataFrame(valid_rows)
        customer_ids = valid_df["customer_id"].dropna().astype(int).unique().tolist()

        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT id FROM customers WHERE id IN :ids"),
                {"ids": tuple(customer_ids)},
            )
            existing_customer_ids = {row[0] for row in result}

        orphan_mask = valid_df["customer_id"].astype(int).apply(
            lambda cid: cid not in existing_customer_ids
        )

        orphan_df = valid_df[orphan_mask].copy()
        orphan_df["rejection_reason"] = orphan_df["customer_id"].apply(
            lambda cid: f"customer_id {int(cid)} does not exist in MySQL"
        )
        rejected_rows.extend(orphan_df.to_dict(orient="records"))

        valid_df = valid_df[~orphan_mask]
        valid_rows = valid_df.to_dict(orient="records")

        print(
            f"[5/6] Customer-ID check — "
            f"{len(orphan_df)} row(s) rejected (unknown customer_id)"
        )
    else:
        print("[5/6] Customer-ID check — skipped (no valid rows)")

    cleaned_df = pd.DataFrame(valid_rows)
    rejected_df = pd.DataFrame(rejected_rows)

    cleaned_df.to_csv(CLEANED_FILE, index=False)
    rejected_df.to_csv(REJECTED_FILE, index=False)

    print(f"[6/6] Output written:")
    print(f"      Cleaned  → {CLEANED_FILE}")
    print(f"      Rejected → {REJECTED_FILE}")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"  Total rows read    : {total_read}")
    print(f"  Valid (cleaned)    : {len(valid_rows)}")
    print(f"  Rejected           : {len(rejected_rows)}")
    print("=" * 50)


if __name__ == "__main__":
    main()