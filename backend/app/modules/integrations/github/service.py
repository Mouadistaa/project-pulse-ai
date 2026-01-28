"""
GitHub integration service for syncing data from GitHub repositories.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.modules.integrations.github.client import GitHubClient
from app.modules.integrations.github.mapper import map_pr_to_pull_request, map_repo_to_repository
from app.modules.integrations.models import PullRequest, Repo, Integration
from app.core.logging import logging

logger = logging.getLogger(__name__)


class GitHubService:
    """Service for syncing GitHub data to database."""
    
    def __init__(self, client: GitHubClient = None):
        self.client = client or GitHubClient()
    
    async def sync_repos(
        self, 
        session: AsyncSession, 
        workspace_id: str,
        repo_names: Optional[List[str]] = None
    ) -> int:
        """
        Sync PRs from GitHub repos to database.
        
        Args:
            session: Database session
            workspace_id: Workspace to sync PRs into
            repo_names: Specific repo names (owner/repo) to sync, or None for all user repos
        
        Returns:
            Number of PRs synced
        """
        synced_count = 0
        
        # Get repos to sync
        if repo_names is None:
            # Fetch all user repos
            repos = await self.client.get_user_repos()
            repo_names = [r["full_name"] for r in repos]
        
        for repo_name in repo_names:
            try:
                synced_count += await self._sync_repo(session, workspace_id, repo_name)
            except Exception as e:
                logger.error(f"Failed to sync repo {repo_name}: {e}")
        
        return synced_count
    
    async def _sync_repo(
        self, 
        session: AsyncSession, 
        workspace_id: str, 
        repo_name: str
    ) -> int:
        """Sync a single repo's PRs."""
        synced = 0
        
        parts = repo_name.split("/")
        if len(parts) != 2:
            logger.warning(f"Invalid repo name format: {repo_name}")
            return 0
        
        owner, repo = parts
        
        # Get or create repo record
        result = await session.execute(
            select(Repo).where(
                Repo.external_id == repo_name,
                Repo.workspace_id == workspace_id
            )
        )
        repo_record = result.scalars().first()
        
        if not repo_record:
            try:
                repo_data = await self.client.get_repo(owner, repo)
                mapped = map_repo_to_repository(repo_data)
                repo_record = Repo(
                    workspace_id=workspace_id,
                    external_id=repo_name,
                    name=mapped["name"],
                    url=mapped["url"]
                )
                session.add(repo_record)
                await session.flush()
            except Exception as e:
                logger.error(f"Failed to fetch repo {repo_name}: {e}")
                return 0
        
        # Get PRs
        prs = await self.client.get_repo_pulls(owner, repo)
        
        for pr_data in prs:
            # Get full PR details for additions/deletions
            try:
                full_pr = await self.client.get_pull_request(owner, repo, pr_data["number"])
                pr_data.update(full_pr)
            except Exception:
                pass  # Use partial data
            
            mapped = map_pr_to_pull_request(pr_data)
            
            # Upsert PR
            result = await session.execute(
                select(PullRequest).where(
                    PullRequest.external_id == mapped["external_id"],
                    PullRequest.workspace_id == workspace_id
                )
            )
            existing = result.scalars().first()
            
            if existing:
                existing.raw_data = mapped["raw_data"]
            else:
                new_pr = PullRequest(
                    workspace_id=workspace_id,
                    repo_id=repo_record.id,
                    external_id=mapped["external_id"],
                    raw_data=mapped["raw_data"]
                )
                session.add(new_pr)
            
            synced += 1
        
        await session.commit()
        return synced


async def sync_github_for_integration(
    session: AsyncSession, 
    integration: Integration
) -> int:
    """
    Sync GitHub data for a specific integration.
    
    Args:
        session: Database session
        integration: The GitHub integration to sync
    
    Returns:
        Number of PRs synced
    """
    if integration.type != "GITHUB":
        return 0
    
    service = GitHubService()
    
    # Get repo names from integration config if specified
    repo_names = integration.config.get("repos") if integration.config else None
    
    return await service.sync_repos(
        session=session,
        workspace_id=str(integration.workspace_id),
        repo_names=repo_names
    )
