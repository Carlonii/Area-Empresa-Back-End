# Backend - Blockchain Data Consent Proxy

API robusta para indexação e intermediação de dados de consentimento na blockchain.

## 🚀 Funcionalidades Principais

*   **Indexação Retroativa**: Escaneia a blockchain em busca de novos consentimentos e persiste no banco de dados.
*   **Persistência de Estado**: Rastreia o último bloco sincronizado para garantir que nenhum evento seja perdido.
*   **Integração IPFS**: Automatiza o pinning de dados via Pinata e recupera metadados (nome, email).
*   **Estatísticas Globais**: Fornece métricas agregadas para dashboards de pesquisa.
*   **Monitoramento**: Endpoint de `/health` para verificação de conectividade com Banco e Blockchain.

## 🛠️ Tecnologias

*   **FastAPI**: Framework web moderno e performante.
*   **Web3.py**: Interação com contratos inteligentes.
*   **SQLAlchemy**: ORM para persistência no PostgreSQL.
*   **IPFS/Pinata**: Armazenamento descentralizado e persistente.

## 🔧 Configuração

Crie um arquivo `.env` na raiz da pasta `Back/` com as seguintes variáveis:

```env
DATABASE_URL=postgresql://user:pass@localhost/db
WEB3_PROVIDER_URL=http://localhost:8545
DATA_CONSENT_ADDRESS=0x...
DATA_CONSENT_ABI_PATH=app/abi/data_consent_abi.json
PINATA_JWT=your_jwt_here
# Ou
PINATA_API_KEY=key
PINATA_SECRET_API_KEY=secret
```

## 🏗️ Como Rodar

1. **Instalar Dependências** (Recomendado usar Poetry):
   ```bash
   poetry install
   ```
2. **Executar a API**:
   ```bash
   python main.py
   ```
3. **Executar o Indexador** (Segundo plano):
   ```bash
   python app/services/blockchain_indexer.py
   ```

## 💓 Saúde do Sistema

Acesse `GET /health` para verificar o status técnico da aplicação.
