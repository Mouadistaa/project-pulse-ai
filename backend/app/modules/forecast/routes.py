from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Any
from datetime import date
from app.db.session import get_db
from app.modules.users.routes import get_current_active_user
from app.modules.users.schemas import User
from app.modules.analytics.models import MetricDaily
from app.modules.forecast.model import simulate_delivery

router = APIRouter()

@router.get("/")
async def get_forecast(
    target_date: date,
    backlog_size: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    # Fetch historical throughput
    result = await db.execute(
        select(MetricDaily.throughput)
        .where(MetricDaily.workspace_id == current_user.workspace_id)
        .order_by(desc(MetricDaily.day))
        .limit(30)
    )
    throughput_history = result.scalars().all()
    # Filter None
    throughput_history = [t for t in throughput_history if t is not None]
    if not throughput_history:
        throughput_history = [1] # Fallback
        
    probability = simulate_delivery(throughput_history, backlog_size, target_date)
    
    return {
        "target_date": target_date,
        "backlog_size": backlog_size,
        "probability": probability
    }
