import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.sql import func
from database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    customer_wallet = Column(String, nullable=True, index=True)
    action_type = Column(String, nullable=False)
    result = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee")
    company = relationship("Company")


class AuditLogCreate(BaseModel):
    employee_id: uuid.UUID | None = None
    company_id: uuid.UUID | None = None
    customer_wallet: str | None = None
    action_type: str = Field(..., min_length=1)
    result: str = Field(..., min_length=1)


class AuditLogPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    employee_id: uuid.UUID | None = None
    company_id: uuid.UUID | None = None
    customer_wallet: str | None = None
    action_type: str
    result: str
    timestamp: str
