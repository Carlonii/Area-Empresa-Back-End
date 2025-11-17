# app/users/user_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from . import user_repository, user_model
from utils.image_processor import process_image_base64

def create_new_user(db: Session, user: user_model.UserCreate):
    db_user = user_repository.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Processa a imagem se fornecida (converte AVIF para JPEG automaticamente)
    try:
        processed_image = process_image_base64(user.profile_image_base64)
        # Cria uma cópia dos dados do usuário com a imagem processada
        user_data = user.model_copy()
        user_data.profile_image_base64 = processed_image
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Erro no processamento da imagem: {e}"
        )

    return user_repository.create_user(db=db, user=user_data, role_id=user.role_id)

def get_all_users(db: Session):
    """Serviço para listar todos os usuários. Neste caso, apenas repassa a chamada."""
    return user_repository.get_users(db)

def get_user_by_id(db: Session, user_id: int):
    """Serviço para buscar um usuário pelo ID, com tratamento de erro."""
    db_user = user_repository.get_user(db, user_id=user_id)
    # REGRA DE NEGÓCIO: Se o usuário não for encontrado, retornar um erro 404.
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

def update_existing_user(db: Session, user_id: int, user_in: user_model.UserUpdate):
    """Serviço para atualizar um usuário, com tratamento de erro."""
    db_user = get_user_by_id(db, user_id) # Reutiliza a lógica para buscar e checar se o usuário existe.
    
    # Processa a imagem se fornecida (converte AVIF para JPEG automaticamente)
    if user_in.profile_image_base64:
        try:
            processed_image = process_image_base64(user_in.profile_image_base64)
            # Cria uma cópia dos dados com a imagem processada
            user_data = user_in.model_copy()
            user_data.profile_image_base64 = processed_image
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Erro no processamento da imagem: {e}"
            )
    else:
        user_data = user_in
    
    return user_repository.update_user(db=db, db_user=db_user, user_in=user_data)

def delete_user_by_id(db: Session, user_id: int):
    """Serviço para deletar um usuário, com tratamento de erro."""
    db_user = get_user_by_id(db, user_id) # Reutiliza a lógica para buscar e checar se o usuário existe.
    return user_repository.delete_user(db=db, db_user=db_user)