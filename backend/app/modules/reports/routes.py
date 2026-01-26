from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Any
from app.db.session import get_db
from app.modules.users.routes import get_current_active_user
from app.modules.users.schemas import User
from app.modules.reports.models import Report
from app.modules.reports.generator import generate_draft_report, send_report

router = APIRouter()

@router.post("/generate", response_model=Any)
async def create_report(
    period: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await generate_draft_report(db, str(current_user.workspace_id), period)

@router.get("/", response_model=List[Any])
async def list_reports(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Report)
        .where(Report.workspace_id == current_user.workspace_id)
        .order_by(desc(Report.created_at))
    )
    return result.scalars().all()

@router.post("/{report_id}/approve")
async def approve_report(
    report_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Report).where(Report.id == report_id, Report.workspace_id == current_user.workspace_id))
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    report.status = "APPROVED"
    await db.commit()
    return {"status": "APPROVED"}

@router.post("/{report_id}/send")
async def send_report_endpoint(
    report_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify ownership
    result = await db.execute(select(Report).where(Report.id == report_id, Report.workspace_id == current_user.workspace_id))
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Report not found")
        
    report = await send_report(db, report_id)
    return {"status": report.status}
