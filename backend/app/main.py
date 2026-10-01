from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routes import analytics, auth, customers, health

app = FastAPI(
    title="RetainIQ API",
    description="Customer intelligence and churn prediction backend",
    version="1.0.0",
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