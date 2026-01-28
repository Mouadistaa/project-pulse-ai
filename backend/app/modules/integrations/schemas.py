from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional, Dict, Any

class IntegrationBase(BaseModel):
    type: str  # TRELLO, GITHUB
    name: str
    config: Optional[Dict[str, Any]] = {}
    workspace_id: UUID

class IntegrationCreate(IntegrationBase):
    secrets_ref: Optional[str] = None

class IntegrationUpdate(BaseModel):
    status: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class Integration(IntegrationBase):
    id: UUID
    status: str
    model_config = ConfigDict(from_attributes=True)
