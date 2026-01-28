"""
Trello API Client for fetching boards, cards, and lists.
Uses TRELLO_KEY and TRELLO_TOKEN from environment.
"""
import httpx
from typing import List, Dict, Any, Optional
from app.core.config import settings


class TrelloClient:
    """Client for Trello REST API (read-only operations)."""
    
    BASE_URL = "https://api.trello.com/1"
    
    def __init__(self, api_key: str = None, token: str = None):
        self.api_key = api_key or settings.TRELLO_KEY
        self.token = token or settings.TRELLO_TOKEN
        
    def _auth_params(self) -> Dict[str, str]:
        """Return auth parameters for API calls."""
        return {
            "key": self.api_key,
            "token": self.token
        }
    
    async def get_boards(self) -> List[Dict[str, Any]]:
        """Fetch all boards accessible to the authenticated user."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/members/me/boards",
                params=self._auth_params()
            )
            response.raise_for_status()
            return response.json()
    
    async def get_board(self, board_id: str) -> Dict[str, Any]:
        """Fetch a specific board by ID."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/boards/{board_id}",
                params=self._auth_params()
            )
            response.raise_for_status()
            return response.json()
    
    async def get_board_lists(self, board_id: str) -> List[Dict[str, Any]]:
        """Fetch all lists on a board."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/boards/{board_id}/lists",
                params=self._auth_params()
            )
            response.raise_for_status()
            return response.json()
    
    async def get_board_cards(self, board_id: str) -> List[Dict[str, Any]]:
        """Fetch all cards on a board."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/boards/{board_id}/cards",
                params={**self._auth_params(), "fields": "all"}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_card(self, card_id: str) -> Dict[str, Any]:
        """Fetch a specific card by ID."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/cards/{card_id}",
                params={**self._auth_params(), "fields": "all"}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_card_actions(self, card_id: str, filter: str = "all") -> List[Dict[str, Any]]:
        """Fetch actions (history/activity) for a card."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/cards/{card_id}/actions",
                params={**self._auth_params(), "filter": filter}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_board_members(self, board_id: str) -> List[Dict[str, Any]]:
        """Fetch members of a board."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/boards/{board_id}/members",
                params=self._auth_params()
            )
            response.raise_for_status()
            return response.json()


async def test_connection() -> bool:
    """Test if Trello credentials are valid."""
    if not settings.TRELLO_KEY or not settings.TRELLO_TOKEN:
        return False
    try:
        client = TrelloClient()
        await client.get_boards()
        return True
    except Exception:
        return False
