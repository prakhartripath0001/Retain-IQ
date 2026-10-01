# RetainIQ

RetainIQ is an E-Commerce Customer Intelligence and Churn Prediction Platform built using Next.js, FastAPI, MySQL, and Python. The platform analyzes customer behavior, tracks business performance, groups customers into different segments, and predicts which customers may stop purchasing, enabling businesses to improve customer retention.

## Key Features

*   **E-Commerce Analytics:** Analyze business data such as total revenue, customer count, orders, and purchasing trends.
*   **RFM Analysis:** Understand customer purchasing behavior through Recency, Frequency, and Monetary value calculations.
*   **Customer Segmentation:** Group customers using K-Means clustering into segments like Champions, Loyal Customers, At Risk, and Lost Customers.
*   **Customer Churn Prediction:** Estimate the probability that a customer may stop purchasing (defined as no purchase for 90 days) using Machine Learning.
*   **Model Explainability:** Utilize SHAP to explain which factors contribute to a customer's churn prediction.
*   **Interactive Dashboard:** View analytics, customer history, and churn risk on a comprehensive dashboard.

## Technology Stack

*   **Frontend:** Next.js, TypeScript, Tailwind CSS, shadcn/ui
*   **Backend:** Python, FastAPI
*   **Database:** MySQL, SQLAlchemy, Alembic
*   **Data Science & ML:** Pandas, NumPy, Scikit-learn, XGBoost, SHAP, MLflow
*   **DevOps & Testing:** Docker, GitHub Actions, Pytest, Playwright

## System Architecture

The platform follows a decoupled architecture where the Next.js frontend communicates with the FastAPI backend via HTTP REST APIs. The backend handles data processing, communicates with the MySQL database, and runs machine learning models for predictions. SHAP explanations are generated alongside predictions and delivered to the frontend for transparent insights.

## Getting Started

### Prerequisites

*   Docker and Docker Compose
*   Node.js (for local client development)
*   Python 3.11+ (for local backend development)

### Running with Docker Compose (Recommended)

The easiest way to run the entire RetainIQ stack (Frontend, Backend, and MySQL) is using Docker Compose:

```bash
# Build and start all services in the background
docker compose up -d --build
```

Once running, the services will be available at:
*   **Frontend Client:** http://localhost:3000
*   **Backend API (Swagger Docs):** http://localhost:8000/docs
*   **MySQL Database:** `localhost:3307` (Internal network: `mysql:3306`)

To stop the services:
```bash
docker compose down
```

### Local Development Setup

If you prefer to run the services individually on your host machine or need to install dependencies for your IDE:

#### 1. Setup Pre-commit Hooks (Required)
We use `pre-commit` to enforce code quality (like Ruff linting) before each commit.
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

#### 3. Frontend Client Setup
```bash
cd client
npm install
npm run dev
```

### Data Ingestion

To load sample data into your MySQL database (with built-in validation and cleaning), use the provided data ingestion pipeline:

1. Ensure your MySQL database is running and the schema is applied.
2. Ensure your raw CSV files (e.g., `customers.csv`) are located in `data/raw/`.
3. Activate the backend virtual environment and run the script from the project root:

```bash
source backend/.venv/bin/activate
python scripts/load_data.py
```

This script will validate the CSV schema, clean the records, handle duplicates, upload valid records to MySQL, and output any rejected rows to `data/processed/` for auditing.

## Documentation

* [Database Schema & ER Diagram](docs/database-schema.md)

