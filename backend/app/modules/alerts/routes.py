from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any
from app.db.session import get_db
from app.modules.users.routes import get_current_active_user
from app.modules.users.schemas import User
from app.modules.alerts.service import AlertService

router = APIRouter()
service = AlertService()

@router.get("/", response_model=List[Any])
async def get_alerts(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await service.get_alerts(db, str(current_user.workspace_id))

@router.post("/{alert_id}/ack")
async def acknowledge_alert(
    alert_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    alert = await service.acknowledge_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "ok"}
