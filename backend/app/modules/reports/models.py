from sqlalchemy import String, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.models import Base

class Report(Base):
    __tablename__ = "reports"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status: Mapped[str] = mapped_column(String, default="DRAFT") # DRAFT, APPROVED, SENT
    content: Mapped[str] = mapped_column(Text)
    sources_json: Mapped[dict] = mapped_column(JSON, nullable=True)
    prompt_template: Mapped[str] = mapped_column(Text, nullable=True)
    model_info: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[str] = mapped_column(String)
    period: Mapped[str] = mapped_column(String) # e.g. "2023-10-27"
    
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id"))
