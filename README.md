# RetainIQ

RetainIQ is an E-Commerce Customer Intelligence and Churn Prediction Platform built using Next.js, FastAPI, MySQL, MLflow, and Python. The platform analyzes customer behavior, tracks business performance, groups customers into different segments using K-Means clustering, and predicts which customers may stop purchasing using Machine Learning models (Logistic Regression, Random Forest, XGBoost) and SHAP explainability.

---

## Key Features

* **Executive Dashboard:** High-level business KPIs (Total Revenue, Customers, Orders, Churn Rate), revenue distribution charts, and customer segment insights.
* **Customer Intelligence & Profiling:** Detailed customer profiles with lifetime spend, AOV, RFM segment badges, order history, and live ML churn risk scoring.
* **RFM Analysis & K-Means Segmentation:** Group customers into strategic clusters: *Champions*, *Loyal Customers*, *At Risk*, and *Lost Customers*.
* **Machine Learning Churn Prediction:** 90-day inactivity model predicting customer churn probability and risk levels (*HIGH*, *MEDIUM*, *LOW*).
* **MLflow Experiment Tracking & Model Registry:** Complete experiment tracking logging candidate runs (Logistic Regression, Random Forest, XGBoost), hyperparameters, metrics, dataset versions (`v1.0`), and registered production model versions (`churn_prediction_model`).
* **SHAP Explainability & Playbooks:** Identifies key behavioral risk drivers (*Long time since last purchase*, *Reduced purchase frequency*) and suggests automated retention playbooks.
* **Complete REST APIs:** Full CRUD endpoints for Customers, Products, Orders, Payments, Reviews, Analytics, and Churn Predictions.

---

## Technology Stack

* **Frontend:** Next.js (App Router), TypeScript, Tailwind CSS, shadcn/ui, TanStack Query
* **Backend:** Python, FastAPI, SQLAlchemy, Alembic, PyJWT
* **Database:** MySQL 8.0, SQLite (In-Memory Testing)
* **Data Science & ML:** Pandas, NumPy, Scikit-learn, XGBoost, SHAP, Joblib, Streamlit, Plotly, MLflow
* **DevOps & Testing:** Docker, Docker Compose, GitHub Actions, Pytest, Playwright, Pre-commit, Ruff

---

## System Architecture

The platform follows a decoupled architecture where the Next.js frontend communicates with the FastAPI backend via HTTP REST APIs, with MLflow managing ML experiment tracking and model registration.

```
Next.js Frontend (React Query)
          ↓
   FastAPI Backend ↔ MLflow Tracking & Model Registry (Port 5000)
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

The easiest way to run the entire RetainIQ stack (Frontend, Backend, MySQL, and MLflow) is using Docker Compose:

```bash
# Build and start all services in the background
docker compose up -d --build
```

Once running, the services will be available at:
* **Frontend Client:** http://localhost:3000
* **Backend API (Swagger Docs):** http://localhost:8000/docs
* **MLflow Tracking & Model Registry UI:** http://localhost:5000
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

## Automated Test Suites

### Backend Pytest Suite (52 Unit & Integration Tests)
The backend test suite includes 52 unit and integration tests across 10 test modules (Auth, Customers, Products, Orders, Payments, Reviews, Analytics, Predictions, Health) running against an isolated in-memory SQLite database:

```bash
PYTHONPATH=backend pytest backend/test
```

### Frontend Playwright E2E Suite (9 End-to-End Tests)
The frontend test suite includes 9 Playwright browser tests covering sign in/sign up toggle, dashboard metrics, customer directory, product catalog, orders, RFM segments, churn prediction, and business analytics:

```bash
cd client
npx playwright test
```

---

## CI/CD DevOps Pipeline (GitHub Actions)

The repository uses a 5-stage GitHub Actions pipeline (`.github/workflows/ci.yml`) triggered on `git push` or pull request:

```
git push
    ↓
1. Run Tests (Pytest 52 Backend Tests & Playwright E2E Frontend Tests)
    ↓
2. Lint (Ruff Python Code Quality & ESLint Next.js Rules)
    ↓
3. Build (Production Next.js Asset & Bundle Compilation)
    ↓
4. Docker Image (Build & Push Frontend & Backend Containers to ghcr.io)
    ↓
5. Deploy (Automated Staging/Production Rollout & Health Checks)
```

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

### 6. Machine Learning Experiment & MLflow Model Registry
```bash
python scripts/train_churn_model.py
```
This script executes a full ML experiment pipeline:
* **MLflow Experiment:** Logs runs under experiment `churn_prediction`.
* **Candidate Runs:** Logs parameters, validation/test metrics, and artifacts for:
  * **Run 1:** Logistic Regression
  * **Run 2:** Random Forest
  * **Run 3:** XGBoost
* **Dataset Versioning:** Tags dataset version (`v1.0`) and snapshot date.
* **Model Registry:** Registers top validation performer (e.g. `Logistic Regression`, Validation PR-AUC `0.7754`) into MLflow Model Registry as **`churn_prediction_model` Version 1**.

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
