from app.modules.reports.models import Report
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.modules.analytics.models import MetricDaily, RiskSignal
from app.modules.alerts.models import Alert
from datetime import datetime
import json

async def generate_draft_report(session: AsyncSession, workspace_id: str, period: str):
    # 1. Gather Context
    # Metrics
    metrics_res = await session.execute(
        select(MetricDaily)
        .where(MetricDaily.workspace_id == workspace_id)
        .order_by(desc(MetricDaily.day))
        .limit(7)
    )
    metrics = metrics_res.scalars().all()
    
    # Risks
    risks_res = await session.execute(
        select(RiskSignal).where(RiskSignal.workspace_id == workspace_id).limit(5)
    )
    risks = risks_res.scalars().all()
    
    # Alerts
    alerts_res = await session.execute(
        select(Alert).where(Alert.workspace_id == workspace_id, Alert.status == 'NEW')
    )
    alerts = alerts_res.scalars().all()
    
    # 2. Construct Prompt inputs (Provenance)
    sources = {
        "metrics_count": len(metrics),
        "risks_count": len(risks),
        "alerts_count": len(alerts),
        "metrics_sample": [m.lead_time_p85 for m in metrics] if metrics else []
    }
    
    prompt_template = "Summarize engineering health based on input metrics."
    
    # 3. Generate Content (Mock LLM)
    # In real app, call OpenAI here if env enabled
    content = f"# Engineering Report ({period})\n\n"
    content += "## Executive Summary\n"
    content += "Team velocity is stable with slight risks in lead time.\n\n"
    content += "## Key Metrics\n"
    if metrics:
        content += f"- Lead Time P85: {metrics[0].lead_time_p85:.1f}h\n"
        content += f"- Throughput: {metrics[0].throughput:.1f} prs/day\n"
    
    content += "\n## Risks\n"
    for r in risks:
        content += f"- **{r.type}**: {r.explanation}\n"
        
    # 4. Save DRAFT
    report = Report(
        workspace_id=workspace_id,
        status="DRAFT",
        content=content,
        sources_json=sources,
        prompt_template=prompt_template,
        model_info="mock-gpt-4", # or real model name
        created_at=datetime.utcnow().isoformat(),
        period=period
    )
    session.add(report)
    await session.commit()
    await session.refresh(report)
    return report

async def send_report(session: AsyncSession, report_id: str):
    report = await session.get(Report, report_id)
    if report:
        report.status = "SENT"
        # Stub notification logic here (Email/Slack)
        await session.commit()
    return report
