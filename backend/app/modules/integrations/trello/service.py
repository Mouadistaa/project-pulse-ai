"""
Trello integration service for syncing data from Trello boards.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.modules.integrations.trello.client import TrelloClient
from app.modules.integrations.trello.mapper import map_card_to_work_item
from app.modules.integrations.models import TrelloCard, Integration
from app.core.logging import logging

logger = logging.getLogger(__name__)


class TrelloService:
    """Service for syncing Trello data to database."""
    
    def __init__(self, client: TrelloClient = None):
        self.client = client or TrelloClient()
    
    async def sync_boards(
        self, 
        session: AsyncSession, 
        workspace_id: str,
        board_ids: Optional[List[str]] = None
    ) -> int:
        """
        Sync cards from Trello boards to database.
        
        Args:
            session: Database session
            workspace_id: Workspace to sync cards into
            board_ids: Specific board IDs to sync, or None for all accessible boards
        
        Returns:
            Number of cards synced
        """
        synced_count = 0
        
        # Get board IDs to sync
        if board_ids is None:
            # Use configured board IDs or fetch all
            board_ids = settings.trello_board_ids_list
            if not board_ids:
                # Fetch all accessible boards
                boards = await self.client.get_boards()
                board_ids = [b["id"] for b in boards]
        
        for board_id in board_ids:
            try:
                synced_count += await self._sync_board(session, workspace_id, board_id)
            except Exception as e:
                logger.error(f"Failed to sync board {board_id}: {e}")
        
        return synced_count
    
    async def _sync_board(
        self, 
        session: AsyncSession, 
        workspace_id: str, 
        board_id: str
    ) -> int:
        """Sync a single board's cards."""
        synced = 0
        
        # Get lists to map list IDs to names
        lists = await self.client.get_board_lists(board_id)
        list_map = {lst["id"]: lst["name"] for lst in lists}
        
        # Get all cards on board
        cards = await self.client.get_board_cards(board_id)
        
        for card_data in cards:
            # Map to our format
            list_name = list_map.get(card_data.get("idList"), "Unknown")
            work_item = map_card_to_work_item(card_data, list_name)
            
            # Upsert card
            result = await session.execute(
                select(TrelloCard).where(
                    TrelloCard.external_id == work_item["external_id"],
                    TrelloCard.workspace_id == workspace_id
                )
            )
            existing = result.scalars().first()
            
            if existing:
                # Update
                existing.name = work_item["name"]
                existing.list_name = work_item["list_name"]
                existing.raw_data = work_item["raw_data"]
            else:
                # Insert
                new_card = TrelloCard(
                    workspace_id=workspace_id,
                    external_id=work_item["external_id"],
                    name=work_item["name"],
                    list_name=work_item["list_name"],
                    raw_data=work_item["raw_data"]
                )
                session.add(new_card)
            
            synced += 1
        
        await session.commit()
        return synced


async def sync_trello_for_integration(
    session: AsyncSession, 
    integration: Integration
) -> int:
    """
    Sync Trello data for a specific integration.
    
    Args:
        session: Database session
        integration: The Trello integration to sync
    
    Returns:
        Number of cards synced
    """
    if integration.type != "TRELLO":
        return 0
    
    service = TrelloService()
    
    # Get board IDs from integration config if specified
    board_ids = integration.config.get("board_ids") if integration.config else None
    
    return await service.sync_boards(
        session=session,
        workspace_id=str(integration.workspace_id),
        board_ids=board_ids
    )
