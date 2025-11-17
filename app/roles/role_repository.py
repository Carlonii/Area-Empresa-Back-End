# roles/role_repository.py
from sqlalchemy.orm import Session
from . import role_model

def get_role_by_name(db: Session, name: str):
    return db.query(role_model.Role).filter(role_model.Role.name == name).first()

# Funções básicas do CRUD para Roles
def get_all_roles(db: Session):
    return db.query(role_model.Role).all()

def get_role_by_id(db: Session, role_id: int):
    return db.query(role_model.Role).filter(role_model.Role.id == role_id).first()

def create_role(db: Session, role: role_model.RoleCreate):
    db_role = role_model.Role(name=role.name)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def update_role(db: Session, db_role: role_model.Role, role_in: role_model.RoleUpdate):
    update_data = role_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_role, key, value)
    
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def delete_role(db: Session, db_role: role_model.Role):
    db.delete(db_role)
    db.commit()
    return db_role