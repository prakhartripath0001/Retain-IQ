# RetainIQ

RetainIQ is an E-Commerce Customer Intelligence and Churn Prediction Platform built using Next.js, FastAPI, MySQL, and Python. The platform analyzes customer behavior, tracks business performance, groups customers into different segments using K-Means clustering, and predicts which customers may stop purchasing using Machine Learning models (Random Forest, Logistic Regression, XGBoost) and SHAP explainability.

---

## Key Features

* **Executive Dashboard:** High-level business KPIs (Total Revenue, Customers, Orders, Churn Rate), revenue distribution charts, and customer segment insights.
* **Customer Intelligence & Profiling:** Detailed customer profiles with lifetime spend, AOV, RFM segment badges, order history, and live ML churn risk scoring.
* **RFM Analysis & K-Means Segmentation:** Group customers into strategic clusters: *Champions*, *Loyal Customers*, *At Risk*, and *Lost Customers*.
* **Machine Learning Churn Prediction:** 90-day inactivity model predicting customer churn probability and risk levels (*HIGH*, *MEDIUM*, *LOW*).
* **SHAP Explainability & Playbooks:** Identifies key behavioral risk drivers (*Long time since last purchase*, *Reduced purchase frequency*) and suggests automated retention playbooks.
* **Complete REST APIs:** Full CRUD endpoints for Customers, Products, Orders, Payments, Reviews, Analytics, and Churn Predictions.

---

## Technology Stack

* **Frontend:** Next.js (App Router), TypeScript, Tailwind CSS, shadcn/ui, TanStack Query
* **Backend:** Python, FastAPI, SQLAlchemy, Alembic, PyJWT
* **Database:** MySQL 8.0, SQLite (In-Memory Testing)
* **Data Science & ML:** Pandas, NumPy, Scikit-learn, XGBoost, SHAP, Joblib, Streamlit, Plotly
* **DevOps & Testing:** Docker, GitHub Actions, Pytest, Pre-commit, Ruff

---

## System Architecture

The platform follows a decoupled architecture where the Next.js frontend communicates with the FastAPI backend via HTTP REST APIs. The backend handles data processing, communicates with the MySQL database, and executes machine learning inference pipelines.

```
Next.js Frontend (React Query)
          ↓
   FastAPI Backend
          ↓
 MySQL Database ↔ Scikit-learn ML Model & SHAP Explainer
```

---

## Getting Started

### Prerequisites

* Docker and Docker Compose
* Node.js 18+ (for local frontend development)
* Python 3.11+ (for local backend development)

---

### Running with Docker Compose (Recommended)

The easiest way to run the entire RetainIQ stack (Frontend, Backend, and MySQL) is using Docker Compose:

```bash
# Build and start all services in the background
docker compose up -d --build
```

Once running, the services will be available at:
* **Frontend Client:** http://localhost:3000
* **Backend API (Swagger Docs):** http://localhost:8000/docs
* **MySQL Database:** `localhost:3307` (Internal network: `mysql:3306`)

To stop the services:
```bash
docker compose down
```

---

### Local Development Setup

#### 1. Setup Pre-commit Hooks (Required)
```bash
pip install pre-commit
pre-commit install
```

#### 2. Backend Setup
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirement.txt
uvicorn app.main:app --reload
```

#### Promote Account to Admin (Local Dev)
```bash
docker exec -it retainiq_mysql mysql -uroot -p retainiq -e "UPDATE app_users SET role = 'ADMIN' WHERE email = 'your-email@example.com';"
```

#### 3. Frontend Client Setup
```bash
cd client
npm install
npm run dev
```
Open **http://localhost:3000** in your browser.

---

## Running Pytest Suite

The backend test suite includes 52+ unit and integration tests across 10 test modules (Auth, Customers, Products, Orders, Payments, Reviews, Analytics, Predictions, Health) running against an isolated in-memory SQLite database:

```bash
cd backend
source .venv/bin/activate
pytest
```

---

## Data Pipeline & ML Training

### 1. Data Ingestion
```bash
source backend/.venv/bin/activate
python scripts/load_data.py
```

### 2. Seed Realistic Sample Data
```bash
python scripts/seed_sample_data.py
```

### 3. Exploratory Data Analysis (EDA)
```bash
python scripts/eda.py
```

### 4. RFM Analysis & Segmentation
```bash
python scripts/rfm_analysis.py
python scripts/segment_customers.py
```

### 5. Churn Label & Feature Generation
```bash
export CHURN_SNAPSHOT_DATE="2025-01-01"
export CHURN_DATA_THROUGH_DATE="2025-04-01"
python scripts/generate_churn_labels.py

export FEATURE_SNAPSHOT_DATE="2025-01-01"
python scripts/build_customer_features.py
```

### 6. Train Machine Learning Models
```bash
python scripts/train_churn_model.py
```

---

## REST API Endpoints Overview

| Category | Method | Endpoint | Description |
|---|---|---|---|
| **Predictions** | `POST` | `/api/v1/predictions/churn/{customer_id}` | Live ML churn probability & risk drivers |
| **Analytics** | `GET` | `/api/v1/analytics/overview` | Executive KPI metrics summary |
| | `GET` | `/api/v1/analytics/revenue` | Monthly revenue trends & AOV |
| | `GET` | `/api/v1/analytics/customers` | Customer purchase frequency & avg spend |
| | `GET` | `/api/v1/analytics/segments` | Cluster profiles & segment counts |
| | `GET` | `/api/v1/analytics/churn` | Churn rate & eligible customer metrics |
| **Auth** | `POST` | `/api/v1/auth/register` | Register new user account |
| | `POST` | `/api/v1/auth/login` | Login and obtain JWT token |
| | `GET` | `/api/v1/auth/me` | Fetch current user profile |
| **Customers** | `GET`/`POST`/`PUT`/`DELETE` | `/api/v1/customers` | Full customer CRUD operations |
| **Products** | `GET`/`POST`/`PUT`/`DELETE` | `/api/v1/products` | Full product inventory CRUD |
| **Orders** | `GET`/`POST`/`PUT`/`DELETE` | `/api/v1/orders` | Order processing & line items CRUD |
| **Payments** | `GET`/`POST`/`PUT`/`DELETE` | `/api/v1/payments` | Payment transaction CRUD |
| **Reviews** | `GET`/`POST`/`PUT`/`DELETE` | `/api/v1/reviews` | Product review rating CRUD |

---

## Documentation

* [Database Schema & ER Diagram](docs/database-schema.md)
* [Data Pipeline — Cleaning & Ingestion](docs/data-pipeline.md)
* [Data Science — EDA, RFM & Segmentation](docs/data-science.md)
* [Churn Definition & Label Generation](docs/churn-labels.md)
