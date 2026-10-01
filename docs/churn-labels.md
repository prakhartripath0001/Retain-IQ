# Churn Definition & Label Generation

This document explains how RetainIQ defines customer churn and the reproducible pipeline used to generate churn labels for machine learning.

---

## What is Churn?

For RetainIQ, a customer is considered **churned** if they make **no qualifying purchase in the 90 days following an observation date**.

```
Customer's last purchase
        ↓
Observation Date (snapshot)
        ↓
←————— 90-day label window —————→
        ↓
No purchase → Churn = 1
Purchase   → Churn = 0
```

This creates the binary target variable (`churn`) used to train the machine learning model.

---

## Pipeline Overview

```
MySQL (customers + orders tables)
        ↓
  generate_churn_labels.py
        ↓
  Filter historical orders         ← only orders before snapshot date
        ↓
  Identify eligible customers      ← must have at least 1 historical order
        ↓
  Check future 90-day window       ← did they purchase after snapshot?
        ↓
  Assign label: churn = 0 or 1
        ↓
  reports/churn/churn_labels.csv
```

---

## How to Run

Set the two required environment variables and run from the project root with the backend venv active:

```bash
source backend/.venv/bin/activate

export CHURN_SNAPSHOT_DATE="2025-01-01"
export CHURN_DATA_THROUGH_DATE="2025-04-01"

python scripts/generate_churn_labels.py
```

### Environment Variables

| Variable | Format | Description |
|---|---|---|
| `CHURN_SNAPSHOT_DATE` | `YYYY-MM-DD` | The observation cutoff date. Historical orders are those before this date. |
| `CHURN_DATA_THROUGH_DATE` | `YYYY-MM-DD` | The date through which your order data is complete. Must be at least 90 days after the snapshot date. |

> **Important:** If `CHURN_DATA_THROUGH_DATE` is less than `CHURN_SNAPSHOT_DATE + 90 days`, the script will raise an error and refuse to generate labels. This prevents silently mislabeling customers due to incomplete data.

---

## Churn Label Definition

| Label | Value | Meaning |
|---|---|---|
| Not churned | `0` | Customer placed at least one qualifying order within 90 days of the snapshot |
| Churned | `1` | Customer placed no qualifying orders within 90 days of the snapshot |

### Qualifying purchase statuses

Only orders with one of these statuses count as a purchase:
- `completed`
- `paid`
- `delivered`
- `shipped`

Cancelled or pending orders do not count.

---

## Output: `reports/churn/churn_labels.csv`

| Column | Description |
|---|---|
| `id` | Customer ID |
| `name` | Customer name |
| `email` | Customer email |
| `last_purchase_date` | Most recent qualifying order date before the snapshot |
| `recency_days_at_snapshot` | Days between last purchase and the snapshot date |
| `historical_order_count` | Total qualifying orders placed before snapshot |
| `churn` | **0** = returned within 90 days, **1** = did not return |
| `observation_date` | The snapshot date used |
| `label_window_end` | Snapshot date + 90 days |
| `data_through_date` | The declared data completeness date |
| `label_definition` | Human-readable label rule |

### Sample output

```
========== RETAINIQ CHURN LABELS ==========
Observation date     : 2025-01-01
Data complete through: 2025-04-01
Label window         : 90 days
Eligible customers   : 42

Label counts:
Churned (1)     : 25
Not churned (0) : 17

Saved labels to: reports/churn/churn_labels.csv
```

---

## Eligible Customers

Not all customers receive a label. A customer is **eligible** only if they placed at least one qualifying order **before** the snapshot date. This ensures the model only trains on customers with enough purchase history to make a meaningful prediction.

Customers registered but never ordered are excluded from labeling.

---

## Reproducibility

The pipeline is fully deterministic:
- The same `CHURN_SNAPSHOT_DATE` and `CHURN_DATA_THROUGH_DATE` always produce the same labels given the same database state.
- No randomness is introduced in the labeling step.
- The script can be re-run safely at any time to regenerate labels as more historical data becomes available.

---

## Design Decisions

- **90-day horizon** — Chosen to match a standard retail inactivity threshold. Configurable via `HORIZON_DAYS` in the script.
- **Env vars for dates** — Makes it easy to regenerate labels for different time windows without modifying the script.
- **Data completeness guard** — Prevents a common mistake where the label window extends beyond available data, causing all customers to appear churned.
- **Only historical customers** — The model should only learn from customers who have already demonstrated purchasing behaviour.
