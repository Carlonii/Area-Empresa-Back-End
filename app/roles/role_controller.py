# roles/role_controller.py
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from . import role_service, role_model
from auth.auth_service import require_role, get_current_user

router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/", response_model=role_model.RolePublic, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role("admin"))])
def create_role(role: role_model.RoleCreate, db: Session = Depends(get_db)):
    """Cria um novo perfil (apenas para administradores)."""
    return role_service.create_new_role(db=db, role=role)

@router.get("/", response_model=List[role_model.RolePublic],
            dependencies=[Depends(require_role("admin"))])
def list_roles(db: Session = Depends(get_db)):
    """Lista todos os perfis (apenas para administradores)."""
    return role_service.get_all(db)

@router.get("/{role_id}", response_model=role_model.RolePublic,
            dependencies=[Depends(require_role("admin"))])
def get_role(role_id: int, db: Session = Depends(get_db)):
    """Busca um perfil pelo ID (apenas para administradores)."""
    return role_service.get_role_by_id(db, role_id=role_id)

@router.put("/{role_id}", response_model=role_model.RolePublic,
            dependencies=[Depends(require_role("admin"))])
def update_role(role_id: int, role: role_model.RoleUpdate, db: Session = Depends(get_db)):
    """Atualiza um perfil (apenas para administradores)."""
    return role_service.update_existing_role(db=db, role_id=role_id, role_in=role)

@router.delete("/{role_id}", response_model=role_model.RolePublic,
               dependencies=[Depends(require_role("admin"))])
def delete_role(role_id: int, db: Session = Depends(get_db)):
    """Deleta um perfil (apenas para administradores)."""
    return role_service.delete_role_by_id(db=db, role_id=role_id)