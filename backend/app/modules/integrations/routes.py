from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated, List

from app.db.session import get_db
from app.modules.integrations.models import Integration
from app.modules.integrations.schemas import Integration as IntegrationSchema, IntegrationCreate, IntegrationUpdate
from app.modules.users.routes import get_current_admin_user
from app.modules.users.schemas import User

router = APIRouter()

@router.post("/", response_model=IntegrationSchema)
async def create_integration(
    integration_in: IntegrationCreate,
    current_user: Annotated[User, Depends(get_current_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    # Ensure workspace matches user's workspace
    if integration_in.workspace_id != current_user.workspace_id:
         raise HTTPException(status_code=403, detail="Cannot create integration for another workspace")

    integration = Integration(**integration_in.model_dump())
    db.add(integration)
    await db.commit()
    await db.refresh(integration)
    return integration

@router.get("/", response_model=List[IntegrationSchema])
async def read_integrations(
    current_user: Annotated[User, Depends(get_current_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(Integration).where(Integration.workspace_id == current_user.workspace_id))
    return result.scalars().all()

@router.delete("/{integration_id}")
async def delete_integration(
    integration_id: str,
    current_user: Annotated[User, Depends(get_current_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(Integration).where(Integration.id == integration_id, Integration.workspace_id == current_user.workspace_id))
    integration = result.scalars().first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
        
    await db.delete(integration)
    await db.commit()
    return {"ok": True}
