from sqlalchemy import String, ForeignKey, Float, Date, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid
import datetime
from app.db.models import Base

class MetricDaily(Base):
    __tablename__ = "metrics_daily"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    day: Mapped[datetime.date] = mapped_column(Date, index=True)
    
    lead_time_p50: Mapped[float] = mapped_column(Float, nullable=True)
    lead_time_p85: Mapped[float] = mapped_column(Float, nullable=True)
    wip: Mapped[int] = mapped_column(Float, nullable=True) # Int or Float
    throughput: Mapped[int] = mapped_column(Float, nullable=True)
    review_time_p50: Mapped[float] = mapped_column(Float, nullable=True)
    bug_ratio: Mapped[float] = mapped_column(Float, nullable=True)
    pr_size_p50: Mapped[float] = mapped_column(Float, nullable=True)
    
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id"))

class RiskSignal(Base):
    __tablename__ = "risk_signals"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[str] = mapped_column(String) # DELAY, OVERLOAD, INSTABILITY
    score: Mapped[float] = mapped_column(Float)
    explanation: Mapped[str] = mapped_column(String)
    
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id"))
