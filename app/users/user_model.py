# users/user_model.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from database import Base
from roles.role_model import RolePublic # Importa o schema público de Role
from typing import Optional

# ==================================
# MODELO DA TABELA (SQLAlchemy)
# ==================================
class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, index=True, nullable=True)
    profile_image_url = Column(String, nullable=True)
    profile_image_base64 = Column(Text, nullable=True)
    # Chave estrangeira que aponta para a tabela 'roles'
    role_id = Column(Integer, ForeignKey("roles.id"))
    # Cria a relação para que possamos acessar o objeto Role a partir de um User
    role = relationship("Role")

# ==================================
# SCHEMAS (Pydantic)
# ==================================
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str | None = Field(default=None, min_length=3)
    profile_image_url: Optional[str] = None
    profile_image_base64: Optional[str] = Field(None, description="Imagem em Base64")
    role_id: int = Field(description="ID do role a ser associado ao usuário")

class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=3)
    profile_image_url: Optional[str] = None
    profile_image_base64: Optional[str] = Field(None, description="Imagem em Base64")

class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: EmailStr
    full_name: str | None = None
    profile_image_url: Optional[str] = None
    profile_image_base64: Optional[str] = None
    role: RolePublic # O perfil agora é um objeto aninhado
