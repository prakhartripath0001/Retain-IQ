from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import (
    analytics,
    auth,
    customers,
    health,
    orders,
    payments,
    predictions,
    products,
    reviews,
)

app = FastAPI(
    title="RetainIQ API",
    description="Customer intelligence and churn prediction backend",
    version="1.0.0",
)

# Configure CORS Middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(
    auth.router,
    prefix="/api/v1",
)
app.include_router(
    customers.router,
    prefix="/api/v1",
)
app.include_router(
    products.router,
    prefix="/api/v1",
)
app.include_router(
    orders.router,
    prefix="/api/v1",
)
app.include_router(
    payments.router,
    prefix="/api/v1",
)
app.include_router(
    reviews.router,
    prefix="/api/v1",
)
app.include_router(
    predictions.router,
    prefix="/api/v1",
)
app.include_router(
    analytics.router,
    prefix="/api/v1",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "The request data is invalid.",
            "details": exc.errors(),
        },
    )


@app.get("/")
def root():
    return {
        "app": "RetainIQ",
        "status": "running",
        "docs": "/docs",
    }