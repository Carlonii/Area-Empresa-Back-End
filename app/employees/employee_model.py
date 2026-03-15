import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime
from sqlalchemy.sql import func
from database import Base


class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True) # Now nullable
    wallet_address = Column(String, unique=True, index=True, nullable=True) # Added for wallet auth
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company")


class EmployeeCreate(BaseModel):
    company_id: uuid.UUID | None = None
    wallet_address: str | None = None
    name: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: str | None = None


class EmployeePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID | None
    wallet_address: str | None = None
    name: str
    email: EmailStr
    role: str | None = None
    created_at: datetime


class EmployeeConnectionRequest(Base):
    __tablename__ = "employee_connection_requests"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    status = Column(String, default="pending")  # pending, approved, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee")
    company = relationship("Company")

class EmployeeConnectionRequestCreate(BaseModel):
    company_id: uuid.UUID

class EmployeeConnectionRequestPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    employee_id: uuid.UUID
    company_id: uuid.UUID
    status: str
    created_at: datetime
