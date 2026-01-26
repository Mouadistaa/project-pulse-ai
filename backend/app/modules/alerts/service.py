from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.alerts.models import Alert

class AlertService:
    async def get_alerts(self, db: AsyncSession, workspace_id: str):
        result = await db.execute(select(Alert).where(Alert.workspace_id == workspace_id))
        return result.scalars().all()

    async def acknowledge_alert(self, db: AsyncSession, alert_id: str):
        result = await db.execute(select(Alert).where(Alert.id == alert_id))
        alert = result.scalars().first()
        if alert:
            alert.status = "ACK"
            await db.commit()
            await db.refresh(alert)
        return alert
