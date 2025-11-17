# app/users/user_repository.py

from sqlalchemy.orm import Session
from . import user_model
from security import get_password_hash

# --- FUNÇÕES DE LEITURA (READ) ---

def get_user(db: Session, user_id: int):
    """
    Busca um único usuário pelo seu ID.
    db.query(user_model.User): Inicia uma consulta na tabela User.
    .filter(user_model.User.id == user_id): Filtra os resultados onde o id seja igual ao fornecido.
    .first(): Retorna o primeiro resultado encontrado ou None se não encontrar.
    """
    return db.query(user_model.User).filter(user_model.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    """Busca um único usuário pelo seu e-mail."""
    return db.query(user_model.User).filter(user_model.User.email == email).first()

def get_users(db: Session):
    """
    Busca todos os usuários cadastrados no banco de dados.
    .all(): Retorna uma lista com todos os resultados da consulta.
    """
    return db.query(user_model.User).all()

# --- FUNÇÃO DE CRIAÇÃO (CREATE) ---

def create_user(db: Session, user: user_model.UserCreate, role_id: int = None):
    """
    Cria um novo usuário no banco de dados.
    """
    # Agora a senha é hasheada corretamente
    hashed_password = get_password_hash(user.password)

    # Cria uma instância do modelo SQLAlchemy com os dados do schema Pydantic.
    # É aqui que os dados da API são transformados em um objeto que pode ser salvo no banco.
    db_user = user_model.User(
        email=user.email, 
        hashed_password=hashed_password, 
        full_name=user.full_name,
        profile_image_url=user.profile_image_url,
        profile_image_base64=user.profile_image_base64,
        role_id=role_id
    )

    db.add(db_user)      # Adiciona o novo objeto à sessão (área de preparação).
    db.commit()         # Salva (commita) as mudanças no banco de dados.
    db.refresh(db_user) # Atualiza o objeto db_user com os dados do banco (como o ID gerado).
    return db_user

# --- FUNÇÃO DE ATUALIZAÇÃO (UPDATE) ---

def update_user(db: Session, db_user: user_model.User, user_in: user_model.UserUpdate):
    """Atualiza os dados de um usuário existente."""
    update_data = user_in.model_dump(exclude_unset=True) # Pega só os campos que foram enviados na requisição.
    for key, value in update_data.items():
        # Se o campo for 'password', precisa mapear para 'hashed_password' no modelo SQLAlchemy
        if key == "password":
            setattr(db_user, "hashed_password", value) # AVISO: A senha ainda não está sendo hasheada!
        else:
            setattr(db_user, key, value) # Atualiza cada campo no objeto do banco (db_user).

    db.add(db_user) # Adiciona o objeto modificado à sessão.
    db.commit()     # Salva as alterações.
    db.refresh(db_user) # Atualiza o objeto com os dados do banco.
    return db_user

# --- FUNÇÃO DE DELEÇÃO (DELETE) ---

def delete_user(db: Session, db_user: user_model.User):
    """Deleta um usuário do banco de dados."""
    db.delete(db_user) # Marca o objeto para deleção.
    db.commit()        # Efetiva a deleção no banco.
    return db_user