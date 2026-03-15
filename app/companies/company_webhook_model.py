import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database import Base
from pydantic import BaseModel, ConfigDict, HttpUrl
import uuid as _uuid

class CompanyWebhook(Base):
    __tablename__ = "company_webhooks"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    url = Column(String, nullable=False)
    secret = Column(String, nullable=False)
    events = Column(JSONB, nullable=False, default=[])
    is_active = Column(Boolean, default=True)

class WebhookCreate(BaseModel):
    company_id: _uuid.UUID
    url: HttpUrl
    events: list[str]

class WebhookPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: _uuid.UUID
    company_id: _uuid.UUID
    url: str
    events: list[str]
    is_active: bool
