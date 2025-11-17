# roles/role_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from . import role_repository, role_model

def create_new_role(db: Session, role: role_model.RoleCreate):
    db_role = role_repository.get_role_by_name(db, name=role.name)
    if db_role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role name already exists")
    return role_repository.create_role(db=db, role=role)

def get_all(db: Session):
    return role_repository.get_all_roles(db)

def get_role_by_id(db: Session, role_id: int):
    db_role = role_repository.get_role_by_id(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return db_role

def update_existing_role(db: Session, role_id: int, role_in: role_model.RoleUpdate):
    db_role = get_role_by_id(db, role_id)
    
    # Verificar se o novo nome já existe (se foi alterado)
    if role_in.name != db_role.name:
        existing_role = role_repository.get_role_by_name(db, name=role_in.name)
        if existing_role:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role name already exists")
    
    return role_repository.update_role(db=db, db_role=db_role, role_in=role_in)

def delete_role_by_id(db: Session, role_id: int):
    db_role = get_role_by_id(db, role_id)
    return role_repository.delete_role(db=db, db_role=db_role)