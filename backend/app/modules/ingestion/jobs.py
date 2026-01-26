import asyncio
import random
import uuid
from datetime import datetime, timedelta, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.modules.integrations.models import Integration, Repo, PullRequest, JiraIssue
from app.modules.analytics.metrics import compute_daily_metrics
from app.modules.analytics.risk_engine import compute_risks
from app.core.logging import logging

logger = logging.getLogger(__name__)

async def generate_mock_data(session: AsyncSession, integration: Integration):
    """
    Generates deterministic demo data if MOCK_MODE is enabled.
    """
    workspace_id = integration.workspace_id
    
    # Create or Get Repo
    result = await session.execute(select(Repo).where(Repo.workspace_id == workspace_id))
    repo = result.scalars().first()
    if not repo:
        repo = Repo(
            workspace_id=workspace_id,
            external_id="mock-repo-1",
            name="demo-repo",
            url="https://github.com/demo/repo"
        )
        session.add(repo)
        await session.flush()

    # Generate PRs for the last 30 days
    today = date.today()
    for i in range(30):
        day = today - timedelta(days=i)
        # Random but deterministic based on day
        random.seed(f"{day}-{integration.id}")
        
        num_prs = random.randint(1, 10)
        for j in range(num_prs):
            external_id = f"pr-{day}-{j}"
            # Check exist
            res = await session.execute(select(PullRequest).where(PullRequest.external_id == external_id))
            if res.scalars().first():
                continue
            
            created_at = datetime.combine(day, datetime.min.time()) + timedelta(hours=random.randint(9, 17))
            closed_at = created_at + timedelta(hours=random.randint(1, 48))
            
            pr = PullRequest(
                workspace_id=workspace_id,
                repo_id=repo.id,
                external_id=external_id,
                raw_data={
                    "created_at": created_at.isoformat(),
                    "closed_at": closed_at.isoformat(),
                    "merged_at": closed_at.isoformat(),
                    "additions": random.randint(10, 500),
                    "deletions": random.randint(5, 200),
                    "comments": random.randint(0, 10)
                }
            )
            session.add(pr)
    
    # Generate Jira Issues
    for i in range(30):
        day = today - timedelta(days=i)
        random.seed(f"jira-{day}-{integration.id}")
        
        num_issues = random.randint(1, 5)
        for j in range(num_issues):
            key = f"ISSUE-{i}-{j}"
            # Check exist
            res = await session.execute(select(JiraIssue).where(JiraIssue.key == key))
            if res.scalars().first():
                continue

            created_at = datetime.combine(day, datetime.min.time()) + timedelta(hours=random.randint(9, 17))
            resolved_at = created_at + timedelta(days=random.randint(1, 7))
            
            issue = JiraIssue(
                workspace_id=workspace_id,
                external_id=str(uuid.uuid4()),
                key=key,
                raw_data={
                    "created": created_at.isoformat(),
                    "resolutiondate": resolved_at.isoformat(),
                    "status": "Done",
                    "issuetype": "Bug" if random.random() < 0.3 else "Story"
                }
            )
            session.add(issue)

    await session.commit()

async def sync_workspace(workspace_id: str):
    async with AsyncSessionLocal() as session:
        # 1. Fetch Integrations
        result = await session.execute(select(Integration).where(Integration.workspace_id == workspace_id, Integration.status == "ACTIVE"))
        integrations = result.scalars().all()
        
        for integration in integrations:
            # Check Env for MOCK_MODE (simplified for MVP)
            if os.getenv("MOCK_MODE", "false").lower() == "true":
                await generate_mock_data(session, integration)
            else:
                # Real sync logic would go here
                pass
        
        # 2. Compute Metrics
        await compute_daily_metrics(session, workspace_id)
        
        # 3. Compute Risk Signals & Alerts
        await compute_risks(session, workspace_id)

def sync_data_job():
    """
    RQ Job Entry point. Needs to run async code synchronously.
    In a real app we might pass workspace_id. For MVP let's sync all workspaces or a specific one.
    Let's assume we iterate all workspaces or pass one.
    """
    # For MVP, just sync all workspaces with active integrations
    async def run_all():
        async with AsyncSessionLocal() as session:
             # This is a bit hacky for "sync all", ideally we enqueue one job per workspace
             # But let's just find one workspace to demo
             from app.modules.users.models import Workspace
             result = await session.execute(select(Workspace))
             workspaces = result.scalars().all()
             for w in workspaces:
                 await sync_workspace(w.id)
    
    import os
    asyncio.run(run_all())
