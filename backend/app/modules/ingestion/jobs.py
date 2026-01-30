import asyncio
import random
from datetime import datetime, timedelta, date, timezone
from typing import Callable, Awaitable, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.logging import logging
from app.db.session import AsyncSessionLocal
from app.modules.integrations.models import (
    Integration,
    Repo,
    PullRequest,
    TrelloCard,
    IntegrationType,
    IntegrationStatus,
)
from app.modules.integrations.github.service import sync_github_for_integration
from app.modules.integrations.trello.service import sync_trello_for_integration
from app.modules.analytics.metrics import compute_daily_metrics
from app.modules.analytics.risk_engine import compute_risks


logger = logging.getLogger(__name__)


async def _retry(
    fn: Callable[[], Awaitable[Any]],
    *,
    attempts: int = 5,
    base_delay_s: float = 1.0,
    max_delay_s: float = 20.0,
    jitter: float = 0.2,
    label: str = "operation",
):
    """Exponential backoff + jitter (MVP resiliency)."""
    last_err: Exception | None = None
    for i in range(attempts):
        try:
            return await fn()
        except Exception as e:
            last_err = e
            delay = min(max_delay_s, base_delay_s * (2**i))
            delta = delay * jitter
            delay = delay + random.uniform(-delta, delta)
            logger.warning(f"{label} failed (attempt {i+1}/{attempts}): {e}. retry in {delay:.1f}s")
            await asyncio.sleep(max(0.0, delay))
    raise last_err  # type: ignore[misc]


async def generate_mock_data(session: AsyncSession, integration: Integration):
    """Demo data when MOCK_MODE=true."""
    workspace_id = integration.workspace_id

    result = await session.execute(select(Repo).where(Repo.workspace_id == workspace_id))
    repo = result.scalars().first()
    if not repo:
        repo = Repo(
            workspace_id=workspace_id,
            external_id="mock-repo-1",
            name="demo-repo",
            url="https://github.com/demo/repo",
        )
        session.add(repo)
        await session.flush()

    today = date.today()
    for i in range(30):
        day = today - timedelta(days=i)
        random.seed(f"{day}-{integration.id}")
        num_prs = random.randint(1, 10)
        for j in range(num_prs):
            external_id = f"pr-{day}-{j}"
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
                    "comments": random.randint(0, 10),
                },
            )
            session.add(pr)

    list_names = ["To Do", "In Progress", "In Review", "Done"]
    for i in range(30):
        day = today - timedelta(days=i)
        random.seed(f"trello-{day}-{integration.id}")
        num_cards = random.randint(1, 5)
        for j in range(num_cards):
            card_id = f"card-{i}-{j}"
            res = await session.execute(select(TrelloCard).where(TrelloCard.external_id == card_id))
            if res.scalars().first():
                continue

            created_at = datetime.combine(day, datetime.min.time()) + timedelta(hours=random.randint(9, 17))
            if i > 20:
                list_name = "Done"
            elif i > 10:
                list_name = random.choice(["Done", "In Review", "In Progress"])
            else:
                list_name = random.choice(list_names)

            resolved_at = None
            if list_name == "Done":
                resolved_at = created_at + timedelta(days=random.randint(1, 7))

            card_type = "Bug" if random.random() < 0.3 else random.choice(["Feature", "Task"])

            card = TrelloCard(
                workspace_id=workspace_id,
                external_id=card_id,
                name=f"{card_type}-{i}-{j}: Demo work item",
                list_name=list_name,
                raw_data={
                    "created": created_at.isoformat(),
                    "resolutiondate": resolved_at.isoformat() if resolved_at else None,
                    "status": list_name,
                    "cardtype": card_type,
                    "labels": [card_type.lower()],
                    "due": (created_at + timedelta(days=7)).isoformat() if random.random() > 0.5 else None,
                },
            )
            session.add(card)

    await session.commit()


def _as_integration_type(value: Any) -> str:
    if value is None:
        return ""
    try:
        return str(getattr(value, "value", value)).upper()
    except Exception:
        return str(value).upper()


async def sync_workspace(workspace_id: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Integration).where(
                Integration.workspace_id == workspace_id,
                Integration.status == getattr(IntegrationStatus.ACTIVE, "value", IntegrationStatus.ACTIVE),
            )
        )
        integrations = result.scalars().all()

        for integration in integrations:
            itype = _as_integration_type(integration.type)

            if settings.MOCK_MODE:
                await generate_mock_data(session, integration)
                continue

            if itype == IntegrationType.GITHUB.value:
                await _retry(
                    lambda: sync_github_for_integration(session, integration),
                    label=f"github sync ({integration.name})",
                )
            elif itype == IntegrationType.TRELLO.value:
                await _retry(
                    lambda: sync_trello_for_integration(session, integration),
                    label=f"trello sync ({integration.name})",
                )
            else:
                logger.warning(f"Unknown integration type={integration.type} for integration id={integration.id}")

            cfg = dict(integration.config or {})
            cfg["last_synced_at"] = datetime.now(timezone.utc).isoformat()
            integration.config = cfg
            await session.commit()

        await compute_daily_metrics(session, workspace_id)
        await compute_risks(session, workspace_id)


def sync_data_job():
    """RQ Job entrypoint."""
    async def run_all():
        async with AsyncSessionLocal() as session:
            from app.modules.users.models import Workspace
            result = await session.execute(select(Workspace))
            for w in result.scalars().all():
                try:
                    await sync_workspace(str(w.id))
                except Exception as e:
                    logger.error(f"Sync failed for workspace={w.id}: {e}")

    asyncio.run(run_all())
