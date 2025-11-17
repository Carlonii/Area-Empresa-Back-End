# app/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Configuração da URL do banco baseada no ambiente
APP_PROFILE = os.getenv("APP_PROFILE", "DEV")

if APP_PROFILE == "DEV":
    # URL para desenvolvimento local
    SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost/programacaoiii_db"
else:
    # URL para produção (Render ou outro provedor)
    # Render fornece a variável DATABASE_URL automaticamente
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/mydb")

# 2. Cria a "engine" do SQLAlchemy, que é o ponto de entrada para o banco de dados.
#    Ela gerencia as conexões com o banco.
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 3. Cria uma fábrica de sessões (SessionLocal). Cada instância de SessionLocal
#    será uma sessão com o banco de dados. Pense nela como uma "conversa" temporária.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Cria uma classe Base. Nossos modelos de tabela do SQLAlchemy herdarão desta
#    classe para que o ORM possa gerenciá-los.
Base = declarative_base()

# Esta função é a nossa "Injeção de Dependência".
# O FastAPI vai chamá-la para cada requisição que precisar de uma sessão com o banco.
# A palavra 'yield' entrega a sessão para a rota e, quando a rota termina,
# o código após o 'yield' (db.close()) é executado, garantindo que a conexão seja fechada.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()