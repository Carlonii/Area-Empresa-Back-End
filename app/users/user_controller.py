# app/users/user_controller.py

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from typing import List
from database import SessionLocal, get_db
from . import user_service, user_model
from auth.auth_service import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/", response_model=user_model.UserPublic, status_code=status.HTTP_201_CREATED)
def create_user(user: user_model.UserCreate, db: Session = Depends(get_db)):
    """Endpoint para criar um novo usuário. Recebe os dados validados (user)
    e a sessão do banco (db) através da injeção de dependência."""
    return user_service.create_new_user(db=db, user=user)

@router.get("/", response_model=List[user_model.UserPublic])
def read_users(db: Session = Depends(get_db)):
    """Endpoint para listar todos os usuários."""
    return user_service.get_all_users(db)

@router.get("/{user_id}", response_model=user_model.UserPublic)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Endpoint para buscar um usuário pelo ID."""
    return user_service.get_user_by_id(db, user_id=user_id)

@router.put("/{user_id}", response_model=user_model.UserPublic)
def update_user(user_id: int, user: user_model.UserUpdate, db: Session = Depends(get_db)):
    """Endpoint para atualizar um usuário."""
    return user_service.update_existing_user(db=db, user_id=user_id, user_in=user)

@router.delete("/{user_id}", response_model=user_model.UserPublic)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Endpoint para deletar um usuário."""
    # Busca o usuário antes de excluir, garantindo que o relacionamento role está carregado
    user_to_delete = user_service.get_user_by_id(db, user_id)
    # Cria uma cópia dos dados para retorno
    user_data = user_model.UserPublic.model_validate(user_to_delete)
    # Exclui o usuário
    user_service.delete_user_by_id(db=db, user_id=user_id)
    # Retorna o objeto excluído com status 200
    return user_data