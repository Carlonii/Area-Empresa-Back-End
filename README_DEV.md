# Desenvolvimento local — backend

Este arquivo descreve como iniciar o backend em ambiente de desenvolvimento para o projeto `programacaiii_api`.

Pré-requisitos
- Python 3.11.x instalado (veja `runtime.txt`).
- Docker e Docker Compose (opcional, recomendado para banco de dados).
- (Opcional) `poetry` se preferir usar Poetry localmente.

Opção A — Usando Docker Compose (rápido e reproduzível)
1. Abra o terminal na pasta do projeto:
```powershell
Set-Location 'C:\Users\Administrador\Desktop\Prog 3\programacaiii_api'
```
2. Suba os serviços (Postgres + API):
```powershell
docker compose up --build
```

Isso fará:
- Subir um container Postgres (usuário `postgres`, senha `1234`, DB `programacaoiii_db`).
- Construir a imagem da API usando o `Dockerfile` do projeto e executar `uvicorn` na porta 8000.

Endpoints úteis:
- API local: http://localhost:8000
- Docs OpenAPI: http://localhost:8000/docs

Opção B — Rodando localmente sem Docker
1. Crie e ative um virtualenv:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
2. Instale dependências (usando Poetry):
```powershell
pip install --upgrade pip
pip install poetry
poetry config virtualenvs.create false --local
poetry install
```
3. Prepare o banco de dados (local):
- Você pode instalar Postgres localmente ou usar Docker apenas para o DB:
```powershell
docker run --name programacaaiii-postgres -e POSTGRES_PASSWORD=1234 -e POSTGRES_USER=postgres -e POSTGRES_DB=programacaoiii_db -p 5432:5432 -d postgres:15
```
4. Exporte variável de ambiente para modo DEV e rode a aplicação:
```powershell
$env:APP_PROFILE = "DEV"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Testes
```powershell
pytest -q
```

Observações de segurança
- O `SECRET_KEY` em `app/security.py` atualmente é um valor hard-coded; mantenha-o em variáveis de ambiente em produção.
- Não comite credenciais nem `.env` com segredos no repositório.

Variáveis úteis
- `APP_PROFILE`: `DEV` (padrão) ou `PROD` — controla criação de tabelas e CORS.
- `DATABASE_URL`: conexão com Postgres (ex: `postgresql://user:pass@host:5432/dbname`).
 - `WEB3_PROVIDER_URL`: URL do provedor RPC (ex: `http://127.0.0.1:8545`).
 - `DATA_CONSENT_ADDRESS`: endereço do contrato DataConsent na blockchain.
 - `DATA_CONSENT_ABI_PATH`: caminho para o ABI JSON do contrato (padrão `app/abi/data_consent_abi.json`).

Dependências adicionais
- Se for usar o recurso de verificação na blockchain, instale `web3` no ambiente:
```powershell
pip install web3
```

Se precisar, posso também:
- Gerar um `.env.example` e adaptar `security.py` para usar `SECRET_KEY` via `os.getenv`.
- Adicionar um `Makefile`/scripts para facilitar os comandos locais.
