from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.modules.analytics.models import MetricDaily
from app.modules.integrations.models import PullRequest, TrelloCard
from datetime import date, datetime, timedelta
import statistics

async def compute_daily_metrics(session: AsyncSession, workspace_id: str):
    today = date.today()
    
    # 1. Fetch Data Window (e.g., last 30 days)
    # For MVP we just compute 'today' based on recent activity, or recompute last 7 days.
    # Let's compute for today.
    
    # Lead Time: Created -> Merged (for PRs merged today)
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())
    
    # Fetch PRs merged recently (broaden window to simulate "today's stats" from mock data that might be sparse)
    # Using 7 day window for smoothing
    window_start = today - timedelta(days=7)
    
    result = await session.execute(
        select(PullRequest).where(
            PullRequest.workspace_id == workspace_id,
            # In mock data, raw_data stored as dict, accessed differently depending on DB
            # We will fetch all and filter in python for MVP simplicity with JSON columns
        )
    )
    prs = result.scalars().all()
    
    lead_times = []
    pr_sizes = []
    merged_count = 0
    
    for pr in prs:
        raw = pr.raw_data
        if not raw.get('merged_at'):
            continue
            
        merged_at = datetime.fromisoformat(raw['merged_at'])
        if merged_at.date() < window_start:
            continue
            
        created_at = datetime.fromisoformat(raw['created_at'])
        lead_times.append((merged_at - created_at).total_seconds() / 3600) # Hours
        pr_sizes.append(raw.get('additions', 0) + raw.get('deletions', 0))
        merged_count += 1

    lead_time_p50 = statistics.median(lead_times) if lead_times else 0
    lead_time_p85 = statistics.quantiles(lead_times, n=100)[84] if len(lead_times) >= 100 else (max(lead_times) if lead_times else 0)
    pr_size_p50 = statistics.median(pr_sizes) if pr_sizes else 0
    throughput = merged_count / 7 # Daily average over window
    
    # WIP: Open PRs
    result = await session.execute(
        select(func.count()).where(
            PullRequest.workspace_id == workspace_id,
            # JSON logic tricky in generic SQL, assuming raw_data text check or fetch all
        )
    )
    # Fetch all open PRs
    open_prs_count = 0
    for pr in prs:
        raw = pr.raw_data
        if not raw.get('closed_at'):
            open_prs_count += 1
            
    wip = open_prs_count
    
    # Bug Ratio: Bugs / Total Cards Resolved (from Trello cards)
    result = await session.execute(select(TrelloCard).where(TrelloCard.workspace_id == workspace_id))
    cards = result.scalars().all()
    
    bugs = 0
    total_resolved = 0
    for card in cards:
        raw = card.raw_data
        # Check if card is in a "done" state
        status = raw.get('status', card.list_name or '')
        if status.lower() in ['done', 'resolved', 'closed', 'complete']:
            res_date_str = raw.get('resolutiondate')
            if res_date_str:
                try:
                    res_date = datetime.fromisoformat(res_date_str).date()
                    if res_date >= window_start:
                        total_resolved += 1
                        card_type = raw.get('cardtype', '').lower()
                        if card_type == 'bug':
                            bugs += 1
                except (ValueError, TypeError):
                    pass
    
    bug_ratio = (bugs / total_resolved) if total_resolved > 0 else 0
    
    # Review Time (approx as (Closed - Created) - Lead Time? No, Review time is first comment to merge.
    # MVP: Mock it or use Lead Time proxy
    review_time_p50 = lead_time_p50 * 0.6 # Placeholder
    
    # Upsert MetricDaily
    result = await session.execute(select(MetricDaily).where(MetricDaily.workspace_id == workspace_id, MetricDaily.day == today))
    metric = result.scalars().first()
    
    if not metric:
        metric = MetricDaily(workspace_id=workspace_id, day=today)
        session.add(metric)
    
    metric.lead_time_p50 = lead_time_p50
    metric.lead_time_p85 = lead_time_p85
    metric.wip = wip
    metric.throughput = throughput
    metric.review_time_p50 = review_time_p50
    metric.bug_ratio = bug_ratio
    metric.pr_size_p50 = pr_size_p50
    
    await session.commit()
