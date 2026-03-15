import uuid
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database import Base
from pydantic import BaseModel, ConfigDict
from datetime import datetime
import uuid as _uuid

class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    message = Column(String, nullable=False)
    type = Column(String, default="INFO") # INFO, WARNING, CRITICAL
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class NotificationCreate(BaseModel):
    company_id: _uuid.UUID
    message: str
    type: str = "INFO"

class NotificationPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: _uuid.UUID
    company_id: _uuid.UUID
    message: str
    type: str
    is_read: bool
    created_at: datetime
