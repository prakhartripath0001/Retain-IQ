
# RetainIQ — Project Requirements

## 1. Introduction

### 1.1 Purpose

RetainIQ is an E-Commerce Customer Intelligence and Churn Prediction Platform designed to analyze customer behavior, understand purchasing patterns, segment customers, and predict customer churn using machine learning.

This document defines the functional and non-functional requirements, technology requirements, data requirements, and expected behavior of the RetainIQ platform.

### 1.2 Project Scope

The platform will provide a dashboard where users can analyze e-commerce business data, explore customer segments, view customer purchase history, and identify customers who may stop purchasing.

The system will use historical customer and transaction data to calculate RFM metrics, perform customer segmentation, and generate churn predictions.

### 1.3 Target Users

The platform is intended for:

- Business Analysts
- E-Commerce Managers
- Marketing Teams
- Customer Retention Teams
- Data Analysts
- System Administrators

## 2. Project Objectives

The main objectives of RetainIQ are:

- Analyze e-commerce sales and customer data.
- Monitor revenue, orders, and customer activity.
- Calculate Recency, Frequency, and Monetary values.
- Segment customers based on purchasing behavior.
- Predict customer churn risk using machine learning.
- Explain churn predictions using SHAP.
- Provide an interactive analytics dashboard.
- Expose application functionality through REST APIs.
- Store business data and prediction results in MySQL.
- Track machine learning experiments and model versions.

## 3. Functional Requirements

Functional requirements describe what the system must do.

### FR-01: User Authentication

The system should allow authorized users to access the platform.

Requirements:

- Users should be able to log in.
- The system should validate user credentials.
- Unauthorized users should not access protected pages or APIs.
- The system should provide a mechanism to log out.
- Passwords must not be stored as plain text.

Authentication and authorization details will be finalized during implementation.

### FR-02: Dashboard Overview

The system shall provide a dashboard displaying important business metrics.

The dashboard should include:

- Total revenue
- Total customers
- Total orders
- Average order value
- Customer segment distribution
- Customer churn statistics
- Revenue trends
- Recent business activity, where data is available

The dashboard should retrieve data from backend APIs.

### FR-03: Revenue Analytics

The system shall provide revenue analytics based on available order and payment data.

Requirements:

- Calculate total revenue.
- Display revenue trends over time.
- Support date-based filtering.
- Display order and sales summaries.
- Provide data suitable for charts and visualizations.

Revenue calculations must use a clearly defined business rule, including how cancelled orders, refunds, and unpaid orders are handled.

### FR-04: Customer Management

The system shall provide customer information and customer search functionality.

Requirements:

- Display a list of customers.
- View individual customer details.
- Search customers using supported fields.
- Support pagination.
- Display customer purchase history.
- Display customer RFM values.
- Display customer segment information.
- Display churn risk when a prediction is available.

### FR-05: Product Management

The system shall provide product information.

Requirements:

- Display available products.
- View product details.
- Display product prices and categories when available.
- Analyze product sales performance.
- Support searching and pagination.

Product creation, editing, and deletion will depend on the final application scope.

### FR-06: Order Management

The system shall provide order information and order history.

Requirements:

- Display orders.
- View individual order details.
- Display order items.
- Display order dates and statuses.
- Display associated customer information.
- Support date and status filters where applicable.

### FR-07: RFM Analysis

The system shall calculate RFM metrics for customers.

RFM represents:

- Recency: Time since the customer's most recent purchase.
- Frequency: Number of purchases during a defined analysis period.
- Monetary: Total customer spending during a defined analysis period.

Requirements:

- Calculate RFM values from eligible transaction data.
- Use a defined reference date and analysis window.
- Store or retrieve calculated customer features.
- Make RFM values available through backend APIs.
- Display RFM information on customer detail pages.

The implementation must define which order statuses and transaction types count toward RFM calculations.

### FR-08: Customer Segmentation

The system shall group customers based on purchasing behavior.

Requirements:

- Prepare customer features for segmentation.
- Apply K-Means clustering.
- Store customer cluster assignments.
- Display customer segment distribution.
- Allow users to explore customers within a segment.
- Display relevant customer metrics for each segment.

Possible business segment labels include:

- Champions
- Loyal Customers
- Potential Loyalists
- New Customers
- At Risk
- Lost Customers

Cluster numbers generated by K-Means must not automatically be treated as business labels. The system must interpret clusters using their measured characteristics and documented business rules.

### FR-09: Customer Churn Prediction

The system shall estimate the likelihood that a customer will stop purchasing.

Initial churn definition:

A customer is considered churned when they make no purchase during the following 90 days, based on the selected prediction reference date and the project's label-generation rules.

Requirements:

- Prepare historical customer data for model training.
- Generate customer features.
- Train and evaluate churn prediction models.
- Generate churn predictions for individual customers.
- Provide churn probabilities when supported by the selected model.
- Categorize risk using documented thresholds.
- Store prediction results and relevant model version information.
- Display prediction results in the dashboard.

The prediction must be based on information available at the prediction reference date. Future information must not leak into the model's training features.

### FR-10: Machine Learning Models

The system shall evaluate multiple models for churn prediction.

Initial models:

- Logistic Regression
- Random Forest
- XGBoost

Requirements:

- Split data into training and testing sets.
- Train the selected candidate models.
- Evaluate models using consistent evaluation data.
- Record model parameters and performance metrics.
- Save the selected trained model.
- Support loading the model for prediction.

The final model will be selected based on measured evaluation results and business requirements.

### FR-11: Model Evaluation

The system shall report appropriate classification metrics.

Required metrics:

- Precision
- Recall
- F1-score
- ROC-AUC
- PR-AUC
- Confusion Matrix

Evaluation requirements:

- Clearly identify the positive class as churn.
- Report the evaluation dataset and relevant time period.
- Compare candidate models using consistent methodology.
- Consider class imbalance when interpreting results.
- Avoid selecting a model based only on accuracy.

### FR-12: Prediction Explainability

The system shall provide explanations for churn predictions using SHAP.

Requirements:

- Calculate feature contributions where supported.
- Identify features that contribute to an individual prediction.
- Display explanations in an understandable format.
- Show relevant customer features alongside the explanation.
- Distinguish model explanations from guaranteed causes of churn.

SHAP explanations describe how features contribute to the model's output. They do not prove that a feature caused a customer to churn.

### FR-13: Analytics API

The backend shall provide REST API endpoints for dashboard analytics.

Planned endpoints include:

- `GET /api/v1/analytics/overview`
- `GET /api/v1/analytics/revenue`
- `GET /api/v1/analytics/customers`
- `GET /api/v1/analytics/segments`
- `GET /api/v1/analytics/churn`

These endpoints shall return structured JSON responses.

### FR-14: Customer API

The backend shall provide APIs for customer information.

Expected capabilities:

- Retrieve a paginated customer list.
- Retrieve customer details.
- Retrieve customer purchase history.
- Retrieve customer RFM metrics.
- Retrieve customer segment information.
- Retrieve available churn prediction results.

Final routes and response schemas will be defined during API design.

### FR-15: Churn Prediction API

The backend shall expose an endpoint for generating a churn prediction for an individual customer.

Planned endpoint:

`POST /api/v1/predictions/churn/{customer_id}`

Requirements:

- Validate the customer identifier.
- Verify that sufficient customer features are available.
- Load the appropriate trained model.
- Generate a prediction and probability when supported.
- Return relevant model information.
- Store prediction history when required.
- Return appropriate errors for invalid customers or unavailable model artifacts.

### FR-16: Data Validation

The system shall validate data before processing it.

Requirements:

- Validate required fields.
- Check data types and formats.
- Handle missing values using documented rules.
- Detect invalid transaction values.
- Validate relationships between customers, orders, and order items.
- Prevent invalid data from silently entering analytics or model training.

### FR-17: Model Tracking

The system shall use MLflow to track machine learning experiments.

Requirements:

- Record experiment names.
- Track model parameters.
- Record evaluation metrics.
- Track model artifacts.
- Record relevant dataset or dataset-version information.
- Maintain model version information.

### FR-18: Reporting and Filtering

The platform should support useful filters for analytics pages.

Expected filters include:

- Date range
- Customer segment
- Churn risk category
- Order status
- Product category

Only filters relevant to the selected page and available data need to be implemented.

## 4. Non-Functional Requirements

Non-functional requirements describe how the system should operate.

### NFR-01: Performance

- API endpoints should respond within an acceptable time under normal workload.
- Database queries should be optimized for common dashboard operations.
- Large datasets should use pagination where appropriate.
- Expensive machine learning operations should not unnecessarily block unrelated requests.
- Performance targets should be measured and documented during testing.

### NFR-02: Security

- Credentials must not be committed to source control.
- Passwords must be securely hashed.
- Protected APIs must enforce appropriate authorization.
- Input validation must be applied to API requests.
- Database credentials must be provided through configuration or environment variables.
- Sensitive information must not be unnecessarily exposed in API responses or logs.

### NFR-03: Reliability

- The application should handle expected errors gracefully.
- Database failures should produce controlled error responses.
- Missing model artifacts should not cause silent failures.
- Invalid requests should return appropriate HTTP status codes.
- Health checks should be provided for application services where applicable.

### NFR-04: Maintainability

- Backend code should be organized into clear modules.
- Business logic should be separated from API route handlers.
- Database models and API schemas should be separated.
- Shared frontend components should be reusable.
- Configuration should be managed consistently.
- Important business rules should be documented.

### NFR-05: Scalability

- Database queries and indexes should support growing datasets.
- APIs should support pagination for large result sets.
- Machine learning training should be separable from online prediction.
- The architecture should allow additional analytics and models to be added later.

### NFR-06: Usability

- The dashboard should have a consistent layout.
- Navigation should make key features easy to find.
- Tables should support readable data presentation.
- Loading, empty, and error states should be displayed.
- Charts should have clear labels and meaningful values.
- Customer risk and model explanations should be understandable to business users.

### NFR-07: Compatibility

- The frontend should support current versions of major desktop browsers.
- The interface should adapt to common screen sizes.
- The backend should expose documented JSON-based REST APIs.

### NFR-08: Testability

- Backend business logic should be testable independently.
- API endpoints should have automated tests.
- Database operations should be tested.
- Machine learning preprocessing and prediction logic should be tested.
- Important frontend workflows should have browser-based tests.

## 5. Technology Requirements

### 5.1 Frontend

- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui

Responsibilities:

- Render the user interface.
- Display dashboard metrics and charts.
- Provide customer, product, and order views.
- Send requests to backend APIs.
- Display analytics and churn predictions.

### 5.2 Backend

- Python
- FastAPI

Responsibilities:

- Provide REST APIs.
- Validate requests.
- Execute business logic.
- Coordinate database operations.
- Access trained machine learning models.
- Return structured JSON responses.

### 5.3 Database

- MySQL

Responsibilities:

- Store application users.
- Store customers and products.
- Store orders and order items.
- Store payments and reviews where available.
- Store customer features and segment assignments.
- Store churn prediction records and model metadata.

### 5.4 ORM and Migrations

- SQLAlchemy
- Alembic

Responsibilities:

- Define database models.
- Manage database queries and persistence.
- Track and apply database schema migrations.

### 5.5 Data Science and Machine Learning

- Pandas
- NumPy
- Scikit-learn
- XGBoost
- SHAP

Responsibilities:

- Clean and transform data.
- Calculate customer features.
- Perform customer segmentation.
- Train and evaluate churn models.
- Explain model predictions.

### 5.6 Testing

- Pytest
- Playwright

Responsibilities:

- Test backend logic and API behavior.
- Test data processing and machine learning utilities.
- Test key frontend workflows through browser automation.

### 5.7 DevOps and Tracking

- Docker
- GitHub Actions
- MLflow

Responsibilities:

- Run services in consistent environments.
- Automate testing and build workflows.
- Track machine learning experiments and model artifacts.

## 6. Database Requirements

The planned database may include the following tables.

### 6.1 Users

Stores application user and authentication information.

Possible fields:

- `id`
- `name`
- `email`
- `password_hash`
- `role`
- `created_at`
- `updated_at`

### 6.2 Customers

Stores customer profile information.

Possible fields:

- `id`
- `name`
- `email`
- `phone`
- `created_at`
- `updated_at`

### 6.3 Products

Stores product information.

Possible fields:

- `id`
- `name`
- `description`
- `category`
- `price`
- `created_at`
- `updated_at`

### 6.4 Orders

Stores customer order information.

Possible fields:

- `id`
- `customer_id`
- `order_date`
- `status`
- `total_amount`
- `created_at`

### 6.5 Order Items

Stores products associated with orders.

Possible fields:

- `id`
- `order_id`
- `product_id`
- `quantity`
- `unit_price`
- `subtotal`

### 6.6 Payments

Stores payment information where available.

Possible fields:

- `id`
- `order_id`
- `amount`
- `payment_method`
- `payment_status`
- `payment_date`

### 6.7 Reviews

Stores customer product reviews where available.

Possible fields:

- `id`
- `customer_id`
- `product_id`
- `rating`
- `review_text`
- `created_at`

### 6.8 Customer Features

Stores calculated customer analytics and machine learning features.

Possible fields:

- `id`
- `customer_id`
- `recency`
- `frequency`
- `monetary`
- `last_purchase_date`
- `calculated_at`

Additional features may be added as the machine learning pipeline develops.

### 6.9 Customer Segments

Stores customer segmentation results.

Possible fields:

- `id`
- `customer_id`
- `cluster_id`
- `segment_name`
- `model_version`
- `created_at`

### 6.10 Churn Predictions

Stores customer churn prediction results.

Possible fields:

- `id`
- `customer_id`
- `churn_probability`
- `risk_category`
- `model_version`
- `predicted_at`

### 6.11 Model Versions

Stores metadata about trained machine learning models.

Possible fields:

- `id`
- `model_name`
- `model_version`
- `model_type`
- `metrics`
- `artifact_reference`
- `created_at`

The final schema, field types, constraints, and relationships will be defined through SQLAlchemy models and Alembic migrations.

## 7. API Requirements

### 7.1 API Format

- Use REST conventions.
- Exchange request and response data in JSON format.
- Use appropriate HTTP methods and status codes.
- Validate incoming request parameters.
- Return consistent error responses.
- Keep API routes versioned under `/api/v1`.

### 7.2 Initial Endpoint Plan

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/analytics/overview` | Retrieve dashboard summary metrics |
| GET | `/api/v1/analytics/revenue` | Retrieve revenue analytics |
| GET | `/api/v1/analytics/customers` | Retrieve customer analytics |
| GET | `/api/v1/analytics/segments` | Retrieve customer segment analytics |
| GET | `/api/v1/analytics/churn` | Retrieve churn analytics |
| POST | `/api/v1/predictions/churn/{customer_id}` | Generate a customer churn prediction |

Additional customer, product, order, authentication, and health-check endpoints will be defined during implementation.

## 8. Frontend Page Requirements

The frontend is expected to contain the following pages.

### 8.1 Login Page

- Accept user credentials.
- Display validation errors.
- Provide feedback for failed login attempts.

### 8.2 Dashboard Page

- Display key business metrics.
- Show revenue trends.
- Show customer segment distribution.
- Show churn summaries.

### 8.3 Customers Page

- Display a customer table.
- Support search and pagination.
- Show relevant customer metrics.

### 8.4 Customer Details Page

- Display customer profile information.
- Show purchase history.
- Show RFM values and segment membership.
- Show available churn predictions and explanations.

### 8.5 Products Page

- Display product information.
- Support search and pagination.
- Show product performance where data is available.

### 8.6 Orders Page

- Display orders and their statuses.
- Show order details and associated items.
- Provide relevant filters.

### 8.7 Segments Page

- Display customer segment summaries.
- Show the number of customers in each segment.
- Allow users to explore customers in a selected segment.

### 8.8 Churn Page

- Display churn-related analytics.
- List customers with available churn predictions.
- Show churn probabilities and risk categories.
- Provide access to prediction explanations.

### 8.9 Analytics Page

- Display business analytics and charts.
- Provide supported date and category filters.
- Present metrics in a clear and consistent format.

## 9. Machine Learning Requirements

### 9.1 Data Preparation

The pipeline shall:

- Load eligible historical data.
- Validate data quality.
- Handle missing values.
- Remove or address invalid records according to documented rules.
- Create customer-level features.
- Prevent target leakage.
- Produce reproducible training and evaluation datasets.

### 9.2 Churn Label Generation

The initial churn definition is based on no purchase during the 90 days following a prediction reference date.

The implementation must define:

- The prediction reference date.
- The historical feature window.
- The future 90-day label window.
- Eligible purchase and order statuses.
- How customers without sufficient observation history are handled.

### 9.3 Training

The training process shall:

- Split the data into training and testing datasets.
- Train baseline classification models.
- Evaluate candidate models.
- Record experiment parameters and results.
- Save the selected model and associated metadata.

### 9.4 Prediction

The prediction service shall:

- Load a compatible trained model.
- Apply the same preprocessing used during training.
- Validate required features.
- Generate a churn prediction.
- Return a probability when supported.
- Associate results with the relevant model version.

### 9.5 Explainability

The explanation service shall use SHAP to describe the contribution of features to a model prediction where supported by the selected model and explainer.

## 10. Testing Requirements

### 10.1 Backend Testing

Pytest shall be used to test:

- Business logic.
- API endpoints.
- Request validation.
- Database operations.
- RFM calculations.
- Customer segmentation utilities.
- Machine learning preprocessing.
- Prediction logic.
- Error handling.

### 10.2 Frontend Testing

Playwright shall be used to test important user workflows, including:

- Login.
- Dashboard loading.
- Customer search.
- Customer details.
- Navigation between pages.
- Viewing customer segments.
- Viewing churn predictions.

### 10.3 Machine Learning Testing

Tests should verify:

- Feature generation produces expected outputs.
- Training and prediction features remain consistent.
- Missing or invalid inputs are handled appropriately.
- Predictions have the expected structure.
- Model artifacts can be loaded.
- Evaluation metrics are calculated correctly.

## 11. Deployment Requirements

### 11.1 Docker

Docker shall be used to package the application services.

The planned services are:

- Frontend
- Backend
- MySQL
- MLflow, when introduced

Docker Compose should provide a consistent local development environment and appropriate service configuration.

### 11.2 Environment Configuration

- Store environment-specific settings outside application source code.
- Do not commit production secrets.
- Configure database connections through environment variables.
- Separate development and production configuration.

### 11.3 Continuous Integration

GitHub Actions should automate applicable workflows such as:

- Backend tests.
- Frontend tests.
- Linting and formatting checks.
- Application builds.
- Additional validation before deployment.

### 11.4 Database Migrations

Alembic shall manage database schema changes.

Migrations should be version-controlled and tested before being applied to important environments.

## 12. Project Structure Requirements

The planned project structure is:

```text
retaiq/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── db/
│   │   └── ml/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── hooks/
│   ├── types/
│   └── public/
├── ml/
├── data/
├── docs/
├── scripts/
├── tests/
├── docker-compose.yml
└── README.md
```

The structure may evolve as the project grows, but the separation between frontend, backend, machine learning, data, documentation, and tests should be maintained.

## 13. Acceptance Criteria

The initial version will be considered functionally complete when the following criteria are met:

- Users can access protected application pages through the implemented authentication flow.
- The dashboard displays metrics calculated from available data.
- Customers, products, and orders can be viewed through the interface.
- Customer RFM metrics can be calculated and retrieved.
- K-Means segmentation can produce customer cluster assignments.
- The system can train and evaluate churn prediction models.
- The system can generate churn predictions for eligible customers.
- Prediction results can be stored and retrieved.
- SHAP explanations can be generated for supported predictions.
- The frontend can retrieve and display backend API responses.
- Backend tests cover critical application functionality.
- Important frontend workflows have automated tests.
- Database migrations can create and update the schema.
- The application services can run in the configured Docker environment.
- Machine learning experiments can be tracked using MLflow when that component is configured.

## 14. Assumptions and Constraints

- The platform requires suitable customer, order, and transaction data.
- Analytics quality depends on data completeness and correctness.
- The initial churn definition uses a 90-day future observation window.
- Training data must contain sufficient historical information to generate valid churn labels.
- Customer segmentation quality depends on feature selection and preprocessing.
- Churn predictions represent model estimates, not guarantees of future behavior.
- Authentication details, user roles, data import methods, and production deployment targets must be finalized during implementation.
- Revenue, refunds, cancelled orders, and eligible purchases must follow documented business rules.
- Actual model performance must be measured on appropriate evaluation data and must not be assumed in advance.

## 15. Future Enhancements

Potential future enhancements include:

- Automated customer retention campaign recommendations.
- Customer lifetime value estimation.
- Product recommendation features.
- Scheduled model retraining.
- Model performance and data drift monitoring.
- Advanced customer cohort analysis.
- Exportable analytics reports.
- Role-based access control.
- Integration with external e-commerce platforms.
- Automated alerts for significant changes in churn risk.

These enhancements are outside the initial scope unless explicitly included in a later development phase.

## 16. Conclusion

RetainIQ will combine e-commerce analytics, customer segmentation, machine learning, and model explainability in a single platform.

The requirements defined in this document provide a foundation for designing the database, implementing backend APIs, developing the frontend dashboard, building the machine learning pipeline, and testing the complete application.

Implementation should proceed incrementally, beginning with the project foundation and data model, followed by analytics, customer segmentation, churn prediction, explainability, and deployment.