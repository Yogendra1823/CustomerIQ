from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from ..dependencies import get_db, get_current_user
from ..models.users import User
from ..core.cache import cache
from ..services.analytics_service import get_dashboard_stats

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
@cache(expire=300)
async def read_dashboard_stats(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get high-level dashboard KPIs: total customers, total revenue, average CLV,
    churn rate, active segment count, revenue growth %, etc.
    """
    return await get_dashboard_stats(db)
