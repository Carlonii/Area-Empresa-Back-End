# Dockerfile para Backend FastAPI
FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema necessárias para o PostgreSQL e Pillow
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de dependências
COPY pyproject.toml poetry.lock* ./

# Instala Poetry
RUN pip install poetry

# Configura Poetry para não criar ambiente virtual (já estamos no container)
RUN poetry config virtualenvs.create false

# Regenera o lock file se necessário e instala dependências
RUN poetry lock || true
RUN poetry install --no-root

# Copia todo o código da aplicação
COPY . .

# Expõe a porta que será usada pelo Render
EXPOSE 8000

# Comando para iniciar a aplicação
# O Render usa a variável de ambiente PORT automaticamente
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}