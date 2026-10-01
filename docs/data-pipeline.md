# Data Pipeline — Cleaning & Ingestion

This document explains the **data cleaning and ingestion approach** used in RetainIQ to bring raw CSV data into the MySQL database reliably and reproducibly.

---

## Pipeline Overview

```
data/raw/*.csv
      ↓
  Python Script
      ↓
  Schema Validation       ← are all required columns present?
      ↓
  Type Coercion           ← numeric, datetime conversion
      ↓
  Row-level Validation    ← missing values, invalid prices, bad quantities
      ↓
  Duplicate Detection     ← based on unique identifier (e.g. order id)
      ↓
  Referential Integrity   ← does customer_id exist in MySQL?
      ↓
  ┌──────────────────────────────────────┐
  │  data/processed/cleaned_*.csv        │  ← valid rows
  │  data/processed/rejected_*.csv       │  ← rejected rows + reason
  └──────────────────────────────────────┘
      ↓
   MySQL (via SQLAlchemy)
```

---

## Scripts

| Script | Purpose |
|---|---|
| `scripts/load_data.py` | Loads and ingests `customers.csv` into the `customers` MySQL table |
| `scripts/clean_orders.py` | Validates and cleans `orders.csv`, cross-checks `customer_id` against MySQL |

---

## How to Run

> **Prerequisites:** MySQL must be running and the backend virtual environment must be active.

From the project root:

```bash
# Activate virtual environment (if not already active)
source backend/.venv/bin/activate

# Load customers
python scripts/load_data.py

# Clean & validate orders
python scripts/clean_orders.py
```

---

## Approach: `load_data.py` (Customers)

### What it does
Reads `data/raw/customers.csv`, cleans and validates the data, then inserts new records into the MySQL `customers` table, skipping any emails that are already present.

### Validation rules applied

| Check | Rule |
|---|---|
| Required columns | `name` and `email` must be present |
| Missing values | Rows with empty `name` or `email` are rejected |
| Email format | Must match `user@domain.ext` pattern |
| Intra-CSV duplicates | Only the first occurrence of each email is kept |
| Database duplicates | Emails already in MySQL are skipped (not rejected) |

### Output
- `data/processed/cleaned_customers.csv` — valid rows that were inserted
- `data/processed/rejected_customers.csv` — rows with their rejection reason

### Sample output
```
Customer ingestion completed.
CSV rows read    : 10
Valid rows       : 9
Rejected rows    : 1
New inserted     : 5
Already existing : 4
```

---

## Approach: `clean_orders.py` (Orders)

### What it does
Reads `data/raw/orders.csv`, validates each row through a 6-step pipeline, cross-checks `customer_id` against the live MySQL `customers` table, then writes cleaned and rejected records to `data/processed/`.

### Validation rules applied

| Step | Check | Rule |
|---|---|---|
| Schema | Required columns | `id`, `customer_id`, `status`, `total_amount`, `created_at` must exist |
| Type coercion | Numeric fields | `id`, `customer_id`, `total_amount` → numeric (coerce errors → NaN) |
| Type coercion | Date fields | `created_at` → datetime (coerce errors → NaT) |
| Row validation | Missing values | Any `NaN` in required fields → rejected |
| Row validation | Invalid price | `total_amount <= 0` → rejected |
| Duplicate detection | Order ID | Duplicate `id` within the CSV → rejected (keep first) |
| Referential integrity | Customer exists | `customer_id` not in MySQL `customers` table → rejected |

### Output
- `data/processed/cleaned_orders.csv` — valid orders ready for database insertion
- `data/processed/rejected_orders.csv` — rejected rows with a `rejection_reason` column

### Sample output
```
[1/6] Read 10 rows from orders.csv
[2/6] Schema OK — all required columns present
[3/6] Type coercion applied (numeric + datetime)
[4/6] Validation complete — 7 valid, 3 rejected so far
[5/6] Customer-ID check — 1 row(s) rejected (unknown customer_id)
[6/6] Output written

==================================================
SUMMARY
==================================================
  Total rows read    : 10
  Valid (cleaned)    : 6
  Rejected           : 4
==================================================
```

---

## Directory Structure

```
Retain-IQ/
├── data/
│   ├── raw/
│   │   ├── customers.csv      ← input raw data
│   │   └── orders.csv         ← input raw data
│   └── processed/
│       ├── cleaned_customers.csv
│       ├── rejected_customers.csv
│       ├── cleaned_orders.csv
│       └── rejected_orders.csv
└── scripts/
    ├── load_data.py           ← customer ingestion
    └── clean_orders.py        ← order cleaning pipeline
```

---

## Design Decisions

- **Read all columns as strings first** — prevents Pandas from silently converting malformed data before validation.
- **Rejected rows are never deleted** — they are always written to `rejected_*.csv` for full auditability.
- **Referential integrity is checked live against MySQL** — not hardcoded, so it always reflects the current database state.
- **Scripts are idempotent** — running them multiple times will not create duplicate records; existing records are detected and skipped.
