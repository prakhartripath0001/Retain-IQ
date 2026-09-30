from fastapi import FastAPI

app = FastAPI(
    title="RetainIQ API",
    description="E-commerce Retention Intelligence API and churn Prediction Platform",
    version="1.0.0",
)

@app.get("/")
def root():
    return {
        "message": "Welcome to RetainIQ API!",
        "status": "Running",
        }

@app.get("/health")
def health_check():
    return {
        "message": "RetainIQ API is healthy and running!",
        "status": "Healthy",
        }