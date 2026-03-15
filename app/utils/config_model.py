# utils/config_model.py
from sqlalchemy import Column, String
from database import Base

class SystemConfig(Base):
    """
    Model for storing persistent system configurations/states (e.g. last_block indexed)
    """
    __tablename__ = "system_configs"
    __table_args__ = {'extend_existing': True}
    
    key = Column(String, primary_key=True, index=True)
    value = Column(String, nullable=False)
