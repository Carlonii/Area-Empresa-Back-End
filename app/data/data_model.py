# data/data_model.py
from sqlalchemy import Column, Integer, String, DateTime, UUID
from pydantic import BaseModel, ConfigDict
from database import Base
import uuid
from datetime import datetime
from typing import Optional

# ==================================
# MODELO DA TABELA (SQLAlchemy)
# ==================================
class BlockchainConsent(Base):
    __tablename__ = "blockchain_consents"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    owner_address = Column(String, index=True)
    cid = Column(String, nullable=True) # CID can be null for access events
    full_name = Column(String, index=True, nullable=True)
    email = Column(String, index=True, nullable=True)
    interaction_type = Column(String, index=True, default="REGISTERED") # REGISTERED, GRANTED, REVOKED, REQUESTED, APPROVED
    authorized_address = Column(String, index=True, nullable=True) # Company/User address involved
    timestamp = Column(DateTime, default=datetime.utcnow)
    tx_hash = Column(String, unique=True, index=True)

# ==================================
# SCHEMAS (Pydantic)
# ==================================
class BlockchainConsentCreate(BaseModel):
    owner_address: str
    cid: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    interaction_type: str = "REGISTERED"
    authorized_address: Optional[str] = None
    timestamp: datetime
    tx_hash: str

class BlockchainConsentPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    owner_address: str
    cid: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    interaction_type: str
    authorized_address: Optional[str] = None
    timestamp: datetime
    tx_hash: str
