from sqlalchemy import String, ForeignKey, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from app.db.models import Base

class IntegrationType(str, enum.Enum):
    JIRA = "JIRA"
    GITHUB = "GITHUB"

class IntegrationStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"

class Integration(Base):
    __tablename__ = "integrations"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[IntegrationType] = mapped_column(String)
    status: Mapped[IntegrationStatus] = mapped_column(String, default=IntegrationStatus.ACTIVE)
    name: Mapped[str] = mapped_column(String)
    secrets_ref: Mapped[str] = mapped_column(String, nullable=True)  # Reference to secret store or encrypted
    config: Mapped[dict] = mapped_column(JSON, default={})
    
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id"))
    workspace = relationship("Workspace", back_populates="integrations")

class Repo(Base):
    __tablename__ = "repos"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String)
    url: Mapped[str] = mapped_column(String)
    
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id"))

class PullRequest(Base):
    __tablename__ = "pull_requests"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id: Mapped[str] = mapped_column(String, index=True)
    raw_data: Mapped[dict] = mapped_column(JSON)
    
    repo_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("repos.id"))
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id"))

class JiraIssue(Base):
    __tablename__ = "jira_issues"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id: Mapped[str] = mapped_column(String, index=True)
    key: Mapped[str] = mapped_column(String, index=True)
    raw_data: Mapped[dict] = mapped_column(JSON)
    
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id"))
