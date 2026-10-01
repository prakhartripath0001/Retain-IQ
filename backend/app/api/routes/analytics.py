
from fastapi import APIRouter

from app.core.dependencies import AnalystOrAdmin

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/revenue")
def get_revenue(current_user: AnalystOrAdmin):

    return {
        "message": "Access authorized",
        "metric": "revenue",
        "status": "aggregation_not_configured",
    }