import uuid
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database import Base
from pydantic import BaseModel, ConfigDict
from datetime import datetime
import uuid as _uuid

class DataUsageStat(Base):
    __tablename__ = "data_usage_stats"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    action_type = Column(String, nullable=False) # e.g., 'access_request', 'consent_approval'
    count = Column(Integer, default=0)

class DataUsageStatPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: _uuid.UUID
    company_id: _uuid.UUID
    date: datetime
    action_type: str
    count: int
