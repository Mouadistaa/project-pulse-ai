from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from typing import Optional, List

class WorkspaceBase(BaseModel):
    name: str
    slug: str

class WorkspaceCreate(WorkspaceBase):
    pass

class Workspace(WorkspaceBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    workspace_slug: Optional[str] = None # For demo/MVP simplicity to join/create workspace

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None

class User(UserBase):
    id: UUID
    role: str
    is_active: bool
    workspace_id: Optional[UUID] = None
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
