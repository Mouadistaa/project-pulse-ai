"""
Mapper functions to convert Trello API responses to internal models.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime


def map_card_to_work_item(card: Dict[str, Any], list_name: str = None) -> Dict[str, Any]:
    """
    Map a Trello card response to our internal work item format.
    
    Args:
        card: Raw Trello card data from API
        list_name: Name of the list the card is in (e.g., "In Progress", "Done")
    
    Returns:
        Mapped work item data suitable for TrelloCard model
    """
    # Extract creation date from card ID (first 8 chars are hex timestamp)
    created_date = None
    try:
        card_id = card.get("id", "")
        if len(card_id) >= 8:
            timestamp = int(card_id[:8], 16)
            created_date = datetime.fromtimestamp(timestamp).isoformat()
    except (ValueError, TypeError):
        pass
    
    # Determine card type from labels
    labels = card.get("labels", [])
    card_type = "Task"  # Default
    for label in labels:
        label_name = label.get("name", "").lower()
        if "bug" in label_name:
            card_type = "Bug"
            break
        elif "feature" in label_name:
            card_type = "Feature"
            break
    
    # Determine status from list name
    status = list_name or "Unknown"
    is_done = status.lower() in ["done", "complete", "closed", "resolved", "deployed"]
    
    # Resolution date (if done, use dateLastActivity as approximation)
    resolution_date = None
    if is_done and card.get("dateLastActivity"):
        resolution_date = card.get("dateLastActivity")
    
    return {
        "external_id": card.get("id"),
        "name": card.get("name", "Untitled"),
        "list_name": status,
        "raw_data": {
            "created": created_date or card.get("dateLastActivity"),
            "resolutiondate": resolution_date,
            "status": status,
            "cardtype": card_type,
            "labels": [l.get("name", "") for l in labels],
            "due": card.get("due"),
            "description": card.get("desc", ""),
            "url": card.get("url"),
            "closed": card.get("closed", False),
            "idMembers": card.get("idMembers", []),
            "idBoard": card.get("idBoard"),
            "idList": card.get("idList")
        }
    }


def derive_metrics_from_cards(cards: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Derive basic metrics from a list of work items.
    
    Returns:
        Dict with wip, throughput_potential, bug_count, etc.
    """
    wip = 0
    done = 0
    bugs = 0
    
    for card in cards:
        raw = card.get("raw_data", {})
        status = raw.get("status", "").lower()
        
        if status in ["in progress", "doing", "in review", "review"]:
            wip += 1
        elif status in ["done", "complete", "closed", "resolved", "deployed"]:
            done += 1
        
        if raw.get("cardtype", "").lower() == "bug":
            bugs += 1
    
    return {
        "wip": wip,
        "done_count": done,
        "bug_count": bugs,
        "total_cards": len(cards)
    }
