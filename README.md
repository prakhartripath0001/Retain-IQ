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

### Starting the Backend Locally

To run the FastAPI backend locally, execute the following commands from the project root:

```bash
cd backend

# Create environment — normally ek baar
python3 -m venv .venv

# Activate environment
source .venv/bin/activate

# Install project dependencies
python -m pip install -r requirement.txt

# Run the backend
uvicorn app.main:app --reload
```

### Prerequisites

*   Docker and Docker Compose
*   Node.js
*   Python 3.x

### Installation

1. Clone the repository.
2. Install frontend dependencies.
3. Install backend dependencies.
4. Run database migrations.
5. Start the frontend and backend servers.
