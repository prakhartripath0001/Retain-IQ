
# RetainIQ — Project Overview

## 1. Project Summary

RetainIQ is an E-Commerce Customer Intelligence and Churn Prediction Platform built using Next.js, FastAPI, MySQL, and Python.

The platform analyzes customer behavior, tracks business performance, groups customers into different segments, and predicts which customers may stop purchasing.

It helps businesses understand their customers and make better decisions to improve customer retention.

## 2. Problem Statement

E-commerce businesses collect large amounts of data about customers, orders, products, and purchases. However, it can be difficult to understand customer behavior and identify customers who may stop buying.

RetainIQ uses data analysis and machine learning to identify customer patterns, analyze sales, and estimate customer churn risk.

The platform helps businesses identify customers who may need attention and take steps to encourage them to continue purchasing.

## 3. Project Objectives

- Analyze customer and sales data.
- Understand customer purchasing behavior.
- Calculate RFM scores for customers.
- Group customers into different segments.
- Predict customer churn risk using machine learning.
- Explain why a customer has been identified as high risk.
- Display analytics and predictions through a dashboard.
- Provide APIs for communication between the frontend and backend.

## 4. Main Features

### 4.1 E-Commerce Analytics

Analyze business data such as total revenue, number of customers, orders, product performance, and purchasing trends.

### 4.2 RFM Analysis

RFM stands for Recency, Frequency, and Monetary value.

- Recency: How recently a customer made a purchase.
- Frequency: How often a customer makes purchases.
- Monetary: How much money a customer spends.

RFM helps understand customer purchasing behavior and identify valuable or inactive customers.

### 4.3 Customer Segmentation

Group customers based on their purchasing behavior and spending patterns.

The platform will use K-Means clustering to identify groups of customers with similar characteristics.

Possible customer segments include:
- Champions
- Loyal Customers
- Potential Loyalists
- New Customers
- At Risk
- Lost Customers

### 4.4 Customer Churn Prediction

Customer churn means a customer stops purchasing from a business.

The platform will use machine learning to estimate the probability that a customer may stop purchasing.

For the initial version, churn is defined as no purchase during the following 90 days.

### 4.5 Model Explainability

The platform will use SHAP to explain which factors contribute to a customer's churn prediction.

For example, a long time since the last purchase or a decrease in purchase frequency may contribute to a higher churn risk.

### 4.6 Customer Dashboard

The dashboard will display:
- Total revenue
- Total customers
- Total orders
- Customer segments
- Churn risk
- Customer purchasing history
- Analytics charts
- Churn prediction explanations

## 5. Technology Stack

### Frontend
- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui

### Backend
- Python
- FastAPI

### Database
- MySQL

### ORM and Database Migration
- SQLAlchemy
- Alembic

### Data Science
- Pandas
- NumPy

### Machine Learning
- Scikit-learn
- XGBoost

### Explainability
- SHAP

### Testing
- Pytest
- Playwright

### DevOps
- Docker
- GitHub Actions

### Machine Learning Tracking
- MLflow

## 6. System Workflow

The platform will work through the following steps:

1. Collect customer, product, and order data.
2. Clean and validate the data using Python and Pandas.
3. Store and manage the data in MySQL.
4. Analyze customer behavior and calculate RFM values.
5. Group customers using customer segmentation techniques.
6. Prepare data and features for churn prediction.
7. Train and evaluate machine learning models.
8. Use SHAP to explain model predictions.
9. Expose analytics and prediction results through FastAPI.
10. Display the results in the Next.js dashboard.

## 7. System Architecture

The platform will contain the following components:

- Frontend: Provides the user interface and dashboard.
- Backend API: Processes requests and connects application services.
- Database: Stores customer, product, order, and analysis data.
- Machine Learning Model: Predicts customer churn risk.
- Explainability Module: Explains the factors behind predictions.

### Communication Flow

Next.js Frontend
       |
       | HTTP Request
       v
FastAPI Backend
       |
       +------------------+
       |                  |
       v                  v
   MySQL Database     ML Model
                          |
                          v
                   SHAP Explanation
       |
       v
JSON Response
       |
       v
Next.js Dashboard

The frontend sends requests to the backend through API endpoints. The backend processes the requests, accesses the database or machine learning model when required, and returns results to the frontend.

## 8. Database Overview

The planned database may include the following tables:

- Users
- Customers
- Products
- Orders
- Order Items
- Payments
- Reviews
- Customer Features
- Customer Segments
- Churn Predictions
- Model Versions

These tables will help manage business data and store analytical results.

## 9. Machine Learning Approach

The machine learning pipeline will include:

1. Data collection
2. Data cleaning
3. Exploratory data analysis
4. Feature engineering
5. Train-test split
6. Model training
7. Model evaluation
8. Model explainability
9. Prediction and monitoring

The project will begin with Logistic Regression and Random Forest as baseline models and also evaluate XGBoost.

Model performance will be measured using:
- Precision
- Recall
- F1-score
- ROC-AUC
- PR-AUC
- Confusion Matrix

The final model will be selected based on evaluation results and its ability to identify customers who churn.

## 10. Testing and Deployment

Pytest will be used to test backend functions and APIs.

Playwright will be used to test frontend workflows, such as login, dashboard loading, customer search, and churn prediction.

Docker will help run the application services in a consistent environment.

GitHub Actions will automate tasks such as testing, linting, and building the application.

MLflow will track machine learning experiments, performance metrics, and model versions.

## 11. Expected Outcome

RetainIQ aims to provide a complete platform for e-commerce analytics, customer segmentation, and churn prediction.

It will help businesses understand customer behavior, identify customers who may stop purchasing, and make data-driven decisions to improve customer retention.

The accuracy and usefulness of the predictions will depend on the quality of the data, the churn definition, the selected features, and the model evaluation results.