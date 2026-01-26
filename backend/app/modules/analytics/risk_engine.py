from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.modules.analytics.models import MetricDaily, RiskSignal
from app.modules.alerts.models import Alert
from datetime import date

async def compute_risks(session: AsyncSession, workspace_id: str):
    # Fetch recent metrics
    result = await session.execute(
        select(MetricDaily)
        .where(MetricDaily.workspace_id == workspace_id)
        .order_by(desc(MetricDaily.day))
        .limit(2) 
    )
    metrics = result.scalars().all()
    
    if not metrics:
        return

    today_metric = metrics[0]
    prev_metric = metrics[1] if len(metrics) > 1 else None
    
    risks = []
    
    # DELAY: Throughput down AND Lead Time P85 up
    if prev_metric:
        if today_metric.throughput < prev_metric.throughput * 0.9 and today_metric.lead_time_p85 > prev_metric.lead_time_p85 * 1.1:
            risks.append({
                "type": "DELAY",
                "score": 0.8,
                "explanation": "Delivery slowing down: Throughput dropped while Lead Time increased."
            })

    # OVERLOAD: WIP high AND Lead Time up
    if prev_metric:
        if today_metric.wip > prev_metric.wip * 1.1 and today_metric.lead_time_p50 > prev_metric.lead_time_p50 * 1.1:
             risks.append({
                "type": "OVERLOAD",
                "score": 0.9,
                "explanation": "Team potentially overloaded: WIP and Lead Time both increasing."
            })
            
    # INSTABILITY: Bug Ratio high
    if today_metric.bug_ratio > 0.2: # > 20% bugs
        risks.append({
            "type": "INSTABILITY",
            "score": 0.7 + (today_metric.bug_ratio - 0.2),
            "explanation": f"High bug ratio detected: {today_metric.bug_ratio:.1%} of resolved issues are bugs."
        })

    # Clear old risks/alerts for today? Or just append?
    # For MVP, appending simple risks
    existing_risks = await session.execute(select(RiskSignal).where(RiskSignal.workspace_id == workspace_id)) # Should filter by date or active
    # Let's just create new ones
    
    for r in risks:
        # Save Risk
        signal = RiskSignal(
            workspace_id=workspace_id,
            type=r["type"],
            score=r["score"],
            explanation=r["explanation"]
        )
        session.add(signal)
        
        # Create Alert
        alert = Alert(
            workspace_id=workspace_id,
            severity="HIGH" if r["score"] > 0.8 else "MEDIUM",
            title=f"Risk Detected: {r['type']}",
            history=r["explanation"],
            status="NEW"
        )
        session.add(alert)
        
    await session.commit()
