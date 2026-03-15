import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
import uuid as _uuid
from sqlalchemy.sql import func
from database import Base


class Company(Base):
    __tablename__ = "companies"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    cnpj = Column(String, nullable=True, index=True)
    domain = Column(String, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    wallet_address = Column(String, nullable=False, unique=True, index=True)


class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=1)
    cnpj: str | None = None
    domain: str | None = None
    wallet_address: str = Field(..., min_length=10)


class CompanyPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: _uuid.UUID
    name: str
    cnpj: str | None = None
    domain: str | None = None
    wallet_address: str
    created_at: datetime

