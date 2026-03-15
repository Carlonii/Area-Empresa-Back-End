import uuid
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database import Base
from pydantic import BaseModel, ConfigDict
from datetime import datetime
import uuid as _uuid

class CompanyAPIKey(Base):
    __tablename__ = "company_api_keys"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    key_hash = Column(String, nullable=False)
    prefix = Column(String(7), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)

class APIKeyCreate(BaseModel):
    name: str
    company_id: _uuid.UUID

class APIKeyPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: _uuid.UUID
    company_id: _uuid.UUID
    prefix: str
    name: str
    created_at: datetime
    last_used_at: datetime | None = None
    is_active: bool
