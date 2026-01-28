"""
GitHub API Client for fetching repositories and pull requests.
Uses GITHUB_TOKEN from environment.
"""
import httpx
from typing import List, Dict, Any, Optional
from app.core.config import settings


class GitHubClient:
    """Client for GitHub REST API (read-only operations)."""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: str = None):
        self.token = token or settings.GITHUB_TOKEN
        
    def _headers(self) -> Dict[str, str]:
        """Return headers for API calls."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    async def get_user_repos(self, per_page: int = 100) -> List[Dict[str, Any]]:
        """Fetch repositories for the authenticated user."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/user/repos",
                headers=self._headers(),
                params={"per_page": per_page, "sort": "updated"}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_repo(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetch a specific repository."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}",
                headers=self._headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def get_repo_pulls(
        self, 
        owner: str, 
        repo: str, 
        state: str = "all",
        per_page: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch pull requests for a repository."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}/pulls",
                headers=self._headers(),
                params={"state": state, "per_page": per_page, "sort": "updated"}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_pull_request(
        self, 
        owner: str, 
        repo: str, 
        pull_number: int
    ) -> Dict[str, Any]:
        """Fetch a specific pull request with full details."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}/pulls/{pull_number}",
                headers=self._headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def get_pull_reviews(
        self, 
        owner: str, 
        repo: str, 
        pull_number: int
    ) -> List[Dict[str, Any]]:
        """Fetch reviews for a pull request."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}/pulls/{pull_number}/reviews",
                headers=self._headers()
            )
            response.raise_for_status()
            return response.json()


async def test_connection() -> bool:
    """Test if GitHub credentials are valid."""
    if not settings.GITHUB_TOKEN:
        return False
    try:
        client = GitHubClient()
        async with httpx.AsyncClient() as http:
            response = await http.get(
                f"{GitHubClient.BASE_URL}/user",
                headers=client._headers()
            )
            return response.status_code == 200
    except Exception:
        return False
