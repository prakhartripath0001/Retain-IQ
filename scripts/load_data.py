from pathlib import Path
import re
import sys

import pandas as pd
from sqlalchemy import MetaData, Table, inspect, select

# Locate the existing backend package.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.db.session import engine  

SOURCE_FILE = PROJECT_ROOT / "data" / "raw" / "customers.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
CLEANED_FILE = PROCESSED_DIR / "cleaned_customers.csv"
REJECTED_FILE = PROCESSED_DIR / "rejected_customers.csv"

BATCH_SIZE = 500
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"CSV not found: {SOURCE_FILE}\n"
            "Create data/raw/customers.csv first."
        )

    # Read text fields as strings to preserve phone numbers.
    df = pd.read_csv(
        SOURCE_FILE,
        dtype="string",
        keep_default_na=False,
    )

    # Validate the input schema.
    required_columns = {"name", "email"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"CSV is missing required columns: {sorted(missing_columns)}"
        )

    if not df.columns.is_unique:
        raise ValueError("CSV contains duplicate column names.")

    # Normalize values.
    df["name"] = df["name"].str.strip()
    df["email"] = df["email"].str.strip().str.lower()

    if "phone" in df.columns:
        df["phone"] = df["phone"].str.strip()
    else:
        df["phone"] = ""

    valid_records = []
    rejected_records = []
    seen_emails = set()

    # Validate each row and prevent duplicates inside this CSV.
    for row_number, row in enumerate(
        df.to_dict(orient="records"), start=2
    ):
        name = row["name"]
        email = row["email"]
        phone = row["phone"]

        reason = None

        if not name:
            reason = "Missing name"
        elif not email:
            reason = "Missing email"
        elif not EMAIL_PATTERN.match(email):
            reason = "Invalid email format"
        elif email in seen_emails:
            reason = "Duplicate email in CSV"

        if reason:
            rejected_records.append({
                "source_row": row_number,
                "name": name,
                "email": email,
                "phone": phone,
                "reason": reason,
            })
            continue

        seen_emails.add(email)

        valid_records.append({
            "name": name,
            "email": email,
            "phone": phone or None,
        })

    # Check the actual MySQL schema; never create tables here.
    inspector = inspect(engine)

    if not inspector.has_table("customers"):
        raise RuntimeError(
            "The customers table does not exist in the connected database. "
            "Create and verify the database schema before loading data."
        )

    metadata = MetaData()
    customers = Table(
        "customers",
        metadata,
        autoload_with=engine,
    )

    for column_name in ("name", "email"):
        if column_name not in customers.c:
            raise RuntimeError(
                f"MySQL customers table has no '{column_name}' column."
            )

    # This loader only handles the known customer fields.
    # Stop rather than silently omit another required database column.
    supplied_columns = {"name", "email", "phone"}
    missing_required = [
        column.name
        for column in customers.columns
        if (
            not column.nullable
            and not column.primary_key
            and column.server_default is None
            and column.default is None
            and column.name not in supplied_columns
        )
    ]

    if missing_required:
        raise RuntimeError(
            "The customers table has additional required columns: "
            f"{missing_required}. Update the loader to supply them."
        )

    if "phone" not in customers.c:
        # Do not discard phone data if the table cannot store it.
        if any(record["phone"] for record in valid_records):
            raise RuntimeError(
                "CSV contains phone numbers, but the customers table "
                "has no phone column."
            )

        for record in valid_records:
            record.pop("phone")

    # Save cleaned and rejected rows for auditing.
    pd.DataFrame(
        valid_records, columns=["name", "email", "phone"]
    ).to_csv(CLEANED_FILE, index=False)

    pd.DataFrame(
        rejected_records,
        columns=["source_row", "name", "email", "phone", "reason"],
    ).to_csv(REJECTED_FILE, index=False)

    inserted_count = 0
    existing_count = 0

    # Use a transaction for each batch and skip emails already in MySQL.
    for start in range(0, len(valid_records), BATCH_SIZE):
        batch = valid_records[start : start + BATCH_SIZE]

        if not batch:
            continue

        with engine.begin() as connection:
            batch_emails = [record["email"] for record in batch]

            existing_emails = set(
                connection.execute(
                    select(customers.c.email).where(
                        customers.c.email.in_(batch_emails)
                    )
                ).scalars()
            )

            new_records = [
                record
                for record in batch
                if record["email"] not in existing_emails
            ]

            existing_count += len(batch) - len(new_records)

            if new_records:
                connection.execute(
                    customers.insert(),
                    new_records,
                )

                inserted_count += len(new_records)

    print("Customer ingestion completed.")
    print(f"CSV rows read: {len(df)}")
    print(f"Valid rows: {len(valid_records)}")
    print(f"Rejected rows: {len(rejected_records)}")
    print(f"New customers inserted: {inserted_count}")
    print(f"Already-existing customers skipped: {existing_count}")
    print(f"Cleaned CSV: {CLEANED_FILE}")
    print(f"Rejected CSV: {REJECTED_FILE}")


if __name__ == "__main__":
    main()
