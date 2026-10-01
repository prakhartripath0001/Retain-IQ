# Data Science — EDA, RFM Analysis & Customer Segmentation

This document explains the **data science pipeline** used in RetainIQ — from exploratory data analysis (EDA), through RFM scoring, to K-Means customer segmentation and the interactive Streamlit dashboard.

---

## Pipeline Overview

```
MySQL Database
      ↓
  scripts/eda.py              ← Chapter 7: Exploratory Data Analysis
      ↓
  scripts/rfm_analysis.py     ← Chapter 8: RFM Scoring
      ↓
  scripts/segment_customers.py ← Chapter 9: K-Means Segmentation
      ↓
  dashboard/app.py            ← Chapter 9: Streamlit Dashboard
```

---

## How to Run the Full Pipeline

> **Prerequisites:** MySQL must be running, the backend venv must be active, and data must already be seeded.

```bash
# Activate virtual environment (from project root)
source backend/.venv/bin/activate

# (Optional) Seed MySQL with realistic sample data
python scripts/seed_sample_data.py

# Step 1: EDA
python scripts/eda.py

# Step 2: RFM Analysis
python scripts/rfm_analysis.py

# Step 3: Customer Segmentation
python scripts/segment_customers.py

# Step 4: Launch the Dashboard
streamlit run dashboard/app.py
```

---

## Chapter 7 — Exploratory Data Analysis (`scripts/eda.py`)

### What it does
Connects to MySQL, loads the four source tables (`customers`, `orders`, `order_items`, `products`), computes key business metrics, and generates charts and CSV reports saved to `reports/eda/`.

### Key metrics computed

| Metric | Description |
|---|---|
| Total customers | Count of all registered customers |
| Orders with valid amounts | Orders where `total_amount >= 0` |
| Total revenue | Sum of all valid order amounts |
| Average order value | Total revenue / order count |
| Median order value | NumPy median of order amounts |
| Customers with orders | Distinct `customer_id` in valid orders |
| Orders per buying customer | Order count / buying customer count |

### Outputs

| File | Description |
|---|---|
| `reports/eda/eda_summary.txt` | Plain-text summary of key metrics |
| `reports/eda/customer_summary.csv` | Per-customer order count, total spend, last order date |
| `reports/eda/product_performance.csv` | Units sold and revenue per product |
| `reports/eda/monthly_revenue.csv` | Monthly revenue trend |
| `reports/eda/customer_order_distribution.png` | Histogram of orders per customer |
| `reports/eda/monthly_revenue.png` | Revenue trend line chart |
| `reports/eda/product_performance.png` | Top 10 products by units sold (bar chart) |

### Sample output
```
========== DATASET OVERVIEW ==========
customers   : 50
orders      : 246
order_items : 602
products    : 10

========== KEY METRICS ==========
Registered customers       : 50
Orders with valid amounts  : 246
Revenue across orders      : 129899.02
Average order value        : 528.04
Customers with purchases   : 50
Orders per buying customer : 4.92
Median order value         : 444.86
```

---

## Chapter 8 — RFM Analysis (`scripts/rfm_analysis.py`)

### What it does
Calculates **Recency**, **Frequency**, and **Monetary** values for every customer, then scores each dimension on a 1–4 scale and combines them into a composite RFM score.

### RFM definitions

| Dimension | Definition |
|---|---|
| **Recency** | Days since the customer's most recent order |
| **Frequency** | Total number of orders placed |
| **Monetary** | Total amount spent across all orders |

### Scoring logic

- Each dimension is divided into quartiles (1 = worst, 4 = best).
- Recency is inverted — fewer days = higher score.
- RFM Score = R score + F score + M score (range: 3 – 12).

### Outputs

| File | Description |
|---|---|
| `reports/rfm/rfm_scores.csv` | Per-customer R, F, M values and composite score |
| `reports/rfm/rfm_distribution.png` | Distribution charts for each RFM dimension |

---

## Chapter 9 — Customer Segmentation (`scripts/segment_customers.py`)

### What it does
Takes the RFM scores, applies **K-Means clustering** (scikit-learn), and maps each cluster to a named business segment. Results are written to `reports/segmentation/`.

### Segment mapping

| Cluster profile | Segment label |
|---|---|
| High R, High F, High M | Champions |
| High F or M, Medium R | Loyal Customers |
| Low R, Medium F or M | At Risk |
| Low R, Low F, Low M | Lost Customers |

### Outputs

| File | Description |
|---|---|
| `reports/segmentation/customer_segments.csv` | Per-customer RFM values, cluster ID, and segment name |
| `reports/segmentation/cluster_profiles.csv` | Average RFM values per cluster/segment |
| `reports/segmentation/cluster_scatter.png` | Scatter plot of clusters (Recency vs Monetary) |

---

## Chapter 9 — Segmentation Dashboard (`dashboard/app.py`)

### What it does
An interactive Streamlit web dashboard that reads from `reports/segmentation/` and lets you:

- View top-level KPI metrics (total customers, purchasing customers, cluster count).
- Filter by segment using a multi-select control.
- Explore a bar chart of customers per segment.
- Inspect an interactive scatter plot of Recency vs Spending (bubble size = frequency).
- View cluster profile averages in a table.
- Browse individual customer details sorted by spend.
- Download the filtered customer list as a CSV.

### How to launch

```bash
streamlit run dashboard/app.py
```

Dashboard will open at `http://localhost:8501`.

---

## Directory Structure

```
Retain-IQ/
├── scripts/
│   ├── seed_sample_data.py     ← seed MySQL with realistic data
│   ├── eda.py                  ← EDA: metrics + charts
│   ├── rfm_analysis.py         ← RFM scoring
│   └── segment_customers.py    ← K-Means segmentation
├── dashboard/
│   └── app.py                  ← Streamlit dashboard
└── reports/
    ├── eda/                    ← EDA outputs (CSV + PNG)
    ├── rfm/                    ← RFM outputs (CSV + PNG)
    └── segmentation/           ← Segmentation outputs (CSV + PNG)
```

---

## Design Decisions

- **Matplotlib backend set to `Agg`** — charts are saved to disk without requiring a display, making the scripts safe to run on servers or in CI.
- **All scripts are run from the project root** — `Path(__file__).resolve().parents[1]` is used consistently so relative paths always resolve correctly.
- **Dashboard reads from files, not MySQL** — decouples the dashboard from the live database so it can be viewed offline after a segmentation run.
- **Segments are named from cluster profiles** — the mapping from cluster ID to segment label is derived from the relative RFM averages, not hardcoded to a specific cluster number.
