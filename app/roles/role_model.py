# roles/role_model.py
from sqlalchemy import Column, Integer, String
from pydantic import BaseModel, ConfigDict
from database import Base

# Modelo da Tabela SQLAlchemy
class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

# Schema Pydantic para criar um Role
class RoleCreate(BaseModel):
    name: str

    # Validação: nome deve ter pelo menos 3 caracteres
    from pydantic import Field
    name: str = Field(..., min_length=3)

# Schema Pydantic para atualizar um Role
class RoleUpdate(BaseModel):
    name: str
    # Validação: nome deve ter pelo menos 3 caracteres
    from pydantic import Field
    name: str = Field(..., min_length=3)

# Schema Pydantic para dados públicos
class RolePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
