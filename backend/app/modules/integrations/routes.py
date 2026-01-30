from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated, List

from app.db.session import get_db
from app.modules.integrations.models import Integration
from app.modules.integrations.schemas import Integration as IntegrationSchema, IntegrationCreate, IntegrationUpdate
from app.modules.users.routes import get_current_admin_user
from app.modules.users.schemas import User
from app.modules.integrations.github.client import GitHubClient
from app.modules.integrations.trello.client import TrelloClient
router = APIRouter()

@router.get("/validate")
async def validate_tokens(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    results = {"github": {"ok": False}, "trello": {"ok": False}}

    # GitHub
    try:
        gh = GitHubClient()
        user = await gh.get_user()
        results["github"] = {"ok": True, "login": user.get("login")}
    except Exception as e:
        results["github"] = {"ok": False, "error": str(e)}

    # Trello
    try:
        tr = TrelloClient()
        boards = await tr.get_boards()
        results["trello"] = {
            "ok": True,
            "boards": [{"id": b.get("id"), "name": b.get("name")} for b in boards[:10]],
        }
    except Exception as e:
        results["trello"] = {"ok": False, "error": str(e)}

    return results

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
