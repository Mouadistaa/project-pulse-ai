from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Any
from app.db.session import get_db
from app.modules.users.routes import get_current_active_user
from app.modules.users.schemas import User
from app.modules.analytics.models import MetricDaily, RiskSignal

router = APIRouter()

@router.get("/metrics", response_model=List[Any]) # Pydantic schema simplified
async def get_metrics(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MetricDaily)
        .where(MetricDaily.workspace_id == current_user.workspace_id)
        .order_by(desc(MetricDaily.day))
        .limit(30)
    )
    return result.scalars().all()

@router.get("/risks", response_model=List[Any])
async def get_risks(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(RiskSignal)
        .where(RiskSignal.workspace_id == current_user.workspace_id)
        .order_by(desc(RiskSignal.id)) # Should probably have created_at
        .limit(10)
    )
    return result.scalars().all()
