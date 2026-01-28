"""
Mapper functions to convert GitHub API responses to internal models.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime


def map_pr_to_pull_request(pr: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map a GitHub PR response to our internal format.
    
    Args:
        pr: Raw GitHub PR data from API
    
    Returns:
        Mapped PR data suitable for PullRequest model
    """
    return {
        "external_id": str(pr.get("id")),
        "raw_data": {
            "number": pr.get("number"),
            "title": pr.get("title"),
            "state": pr.get("state"),
            "created_at": pr.get("created_at"),
            "updated_at": pr.get("updated_at"),
            "closed_at": pr.get("closed_at"),
            "merged_at": pr.get("merged_at"),
            "draft": pr.get("draft", False),
            "additions": pr.get("additions", 0),
            "deletions": pr.get("deletions", 0),
            "changed_files": pr.get("changed_files", 0),
            "comments": pr.get("comments", 0),
            "review_comments": pr.get("review_comments", 0),
            "user": pr.get("user", {}).get("login"),
            "url": pr.get("html_url"),
            "base_ref": pr.get("base", {}).get("ref"),
            "head_ref": pr.get("head", {}).get("ref")
        }
    }


def map_repo_to_repository(repo: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map a GitHub repo response to our internal format.
    
    Args:
        repo: Raw GitHub repo data from API
    
    Returns:
        Mapped repo data suitable for Repo model
    """
    return {
        "external_id": str(repo.get("id")),
        "name": repo.get("full_name") or repo.get("name"),
        "url": repo.get("html_url") or repo.get("url")
    }


def derive_metrics_from_prs(prs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Derive basic metrics from a list of PRs.
    
    Returns:
        Dict with open_count, merged_count, avg_time_to_merge, etc.
    """
    open_count = 0
    merged_count = 0
    lead_times = []
    
    for pr in prs:
        raw = pr.get("raw_data", {})
        
        if raw.get("state") == "open":
            open_count += 1
        
        if raw.get("merged_at"):
            merged_count += 1
            try:
                created = datetime.fromisoformat(raw["created_at"].replace("Z", "+00:00"))
                merged = datetime.fromisoformat(raw["merged_at"].replace("Z", "+00:00"))
                lead_times.append((merged - created).total_seconds() / 3600)  # Hours
            except (ValueError, TypeError, KeyError):
                pass
    
    avg_lead_time = sum(lead_times) / len(lead_times) if lead_times else 0
    
    return {
        "open_prs": open_count,
        "merged_prs": merged_count,
        "avg_lead_time_hours": avg_lead_time,
        "total_prs": len(prs)
    }
