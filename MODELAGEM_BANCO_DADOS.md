# Modelagem do Banco de Dados - Sistema de Consentimento de Dados Blockchain

## Visão Geral

Este documento descreve a modelagem completa do banco de dados PostgreSQL utilizado no backend do sistema de consentimento de dados baseado em blockchain.

## Diagrama de Relacionamento (ERD)

```mermaid
erDiagram
    ROLES ||--o{ USERS : "has"
    COMPANIES ||--o{ EMPLOYEES : "employs"
    COMPANIES ||--o{ AUDIT_LOGS : "generates"
    EMPLOYEES ||--o{ AUDIT_LOGS : "performs"
    
    ROLES {
        int id PK
        string name UK
    }
    
    USERS {
        int id PK
        string email UK
        string hashed_password
        string full_name
        string profile_image_url
        text profile_image_base64
        int role_id FK
    }
    
    COMPANIES {
        uuid id PK
        string name
        string cnpj
        string wallet_address UK
        datetime created_at
    }
    
    EMPLOYEES {
        uuid id PK
        uuid company_id FK
        string name
        string email UK
        string password_hash
        string role
        datetime created_at
    }
    
    AUDIT_LOGS {
        uuid id PK
        uuid employee_id FK
        uuid company_id FK
        string customer_wallet
        string action_type
        string result
        datetime timestamp
    }
```

---

## Tabelas Detalhadas

### 1. **ROLES** (Perfis de Usuário)

Armazena os diferentes perfis/papéis que os usuários podem ter no sistema.

| Coluna | Tipo | Constraints | Descrição |
|--------|------|-------------|-----------|
| `id` | INTEGER | PRIMARY KEY, INDEX | Identificador único do perfil |
| `name` | STRING | UNIQUE, INDEX, NOT NULL | Nome do perfil (ex: "admin", "user") |

**Relacionamentos:**
- Um Role pode ter múltiplos Users (1:N)

**Índices:**
- `id` (Primary Key)
- `name` (Unique Index)

---

### 2. **USERS** (Usuários do Sistema)

Armazena informações dos usuários finais (clientes) que cadastram seus dados na blockchain.

| Coluna | Tipo | Constraints | Descrição |
|--------|------|-------------|-----------|
| `id` | INTEGER | PRIMARY KEY, INDEX | Identificador único do usuário |
| `email` | STRING | UNIQUE, INDEX, NOT NULL | Email do usuário (login) |
| `hashed_password` | STRING | NOT NULL | Senha criptografada |
| `full_name` | STRING | INDEX, NULLABLE | Nome completo do usuário |
| `profile_image_url` | STRING | NULLABLE | URL da imagem de perfil |
| `profile_image_base64` | TEXT | NULLABLE | Imagem de perfil em Base64 |
| `role_id` | INTEGER | FOREIGN KEY | Referência ao perfil do usuário |

**Relacionamentos:**
- Pertence a um Role (N:1)

**Índices:**
- `id` (Primary Key)
- `email` (Unique Index)
- `full_name` (Index)

**Chaves Estrangeiras:**
- `role_id` → `roles.id`

**Observações:**
- A senha é armazenada com hash para segurança
- Suporta imagem de perfil tanto por URL quanto por Base64
- O usuário possui uma carteira blockchain associada (gerenciada no frontend)

---

### 3. **COMPANIES** (Empresas)

Armazena informações das empresas que solicitam acesso aos dados dos usuários.

| Coluna | Tipo | Constraints | Descrição |
|--------|------|-------------|-----------|
| `id` | UUID | PRIMARY KEY, INDEX | Identificador único da empresa |
| `name` | STRING | NOT NULL | Nome da empresa |
| `cnpj` | STRING | INDEX, NULLABLE | CNPJ da empresa |
| `wallet_address` | STRING | UNIQUE, INDEX, NOT NULL | Endereço da carteira blockchain |
| `created_at` | DATETIME | DEFAULT NOW() | Data de criação do registro |

**Relacionamentos:**
- Possui múltiplos Employees (1:N)
- Gera múltiplos AuditLogs (1:N)

**Índices:**
- `id` (Primary Key)
- `cnpj` (Index)
- `wallet_address` (Unique Index)

**Observações:**
- Cada empresa possui uma carteira blockchain única
- O `wallet_address` é usado para interagir com o smart contract
- Timestamp com timezone para auditoria

---

### 4. **EMPLOYEES** (Funcionários das Empresas)

Armazena informações dos funcionários que trabalham nas empresas e acessam os dados.

| Coluna | Tipo | Constraints | Descrição |
|--------|------|-------------|-----------|
| `id` | UUID | PRIMARY KEY, INDEX | Identificador único do funcionário |
| `company_id` | UUID | FOREIGN KEY, NOT NULL | Referência à empresa |
| `name` | STRING | NOT NULL | Nome do funcionário |
| `email` | STRING | UNIQUE, INDEX, NOT NULL | Email do funcionário (login) |
| `password_hash` | STRING | NOT NULL | Senha criptografada |
| `role` | STRING | NULLABLE | Cargo/função do funcionário |
| `created_at` | DATETIME | DEFAULT NOW() | Data de criação do registro |

**Relacionamentos:**
- Pertence a uma Company (N:1)
- Realiza múltiplos AuditLogs (1:N)

**Índices:**
- `id` (Primary Key)
- `email` (Unique Index)

**Chaves Estrangeiras:**
- `company_id` → `companies.id`

**Observações:**
- Funcionários usam a carteira da empresa para acessar dados
- Sistema de autenticação separado dos usuários finais
- O campo `role` armazena o cargo (diferente do `role_id` dos Users)

---

### 5. **AUDIT_LOGS** (Logs de Auditoria)

Registra todas as ações realizadas no sistema para fins de auditoria e rastreabilidade.

| Coluna | Tipo | Constraints | Descrição |
|--------|------|-------------|-----------|
| `id` | UUID | PRIMARY KEY, INDEX | Identificador único do log |
| `employee_id` | UUID | FOREIGN KEY, NULLABLE | Funcionário que realizou a ação |
| `company_id` | UUID | FOREIGN KEY, NULLABLE | Empresa relacionada à ação |
| `customer_wallet` | STRING | INDEX, NULLABLE | Carteira do cliente acessado |
| `action_type` | STRING | NOT NULL | Tipo de ação realizada |
| `result` | STRING | NOT NULL | Resultado da ação |
| `timestamp` | DATETIME | DEFAULT NOW() | Momento da ação |

**Relacionamentos:**
- Pertence a um Employee (N:1)
- Pertence a uma Company (N:1)

**Índices:**
- `id` (Primary Key)
- `customer_wallet` (Index)

**Chaves Estrangeiras:**
- `employee_id` → `employees.id`
- `company_id` → `companies.id`

**Observações:**
- Registra todas as tentativas de acesso aos dados
- Inclui tanto sucessos quanto falhas
- Permite rastreabilidade completa das operações
- Timestamp com timezone para precisão temporal

---

## Fluxo de Dados

### Cadastro de Usuário (Cliente)

```mermaid
sequenceDiagram
    participant U as Usuário
    participant DB as Database
    participant BC as Blockchain
    
    U->>DB: Cria conta (email, senha, nome)
    DB->>DB: Insere em USERS com role_id
    U->>BC: Registra dados na blockchain
    BC-->>U: Confirmação
```

### Cadastro de Empresa e Funcionário

```mermaid
sequenceDiagram
    participant A as Admin
    participant DB as Database
    
    A->>DB: Cria empresa (nome, CNPJ, wallet)
    DB->>DB: Insere em COMPANIES
    A->>DB: Cria funcionário (nome, email, company_id)
    DB->>DB: Insere em EMPLOYEES
```

### Acesso a Dados por Empresa

```mermaid
sequenceDiagram
    participant E as Employee
    participant DB as Database
    participant BC as Blockchain
    participant AL as AuditLog
    
    E->>DB: Solicita acesso aos dados
    DB->>BC: Verifica autorização
    BC-->>DB: Retorna dados ou erro
    DB->>AL: Registra ação em AUDIT_LOGS
    AL-->>E: Retorna resultado
```

---

## Schemas Pydantic

Cada modelo possui schemas Pydantic para validação de dados:

### User Schemas

- **UserCreate**: Validação para criação de usuário
  - `email`: EmailStr (validado)
  - `password`: min_length=8
  - `full_name`: min_length=3 (opcional)
  - `role_id`: int (obrigatório)
  - `profile_image_url`: opcional
  - `profile_image_base64`: opcional

- **UserUpdate**: Validação para atualização
  - `full_name`: min_length=3 (opcional)
  - `profile_image_url`: opcional
  - `profile_image_base64`: opcional

- **UserPublic**: Dados retornados ao cliente
  - Inclui todos os campos exceto `hashed_password`
  - Inclui objeto `role` aninhado

### Company Schemas

- **CompanyCreate**: Validação para criação
  - `name`: min_length=1
  - `cnpj`: opcional
  - `wallet_address`: min_length=10

- **CompanyPublic**: Dados retornados
  - Todos os campos incluindo `created_at`

### Employee Schemas

- **EmployeeCreate**: Validação para criação
  - `company_id`: UUID
  - `name`: min_length=1
  - `email`: EmailStr
  - `password`: min_length=8
  - `role`: opcional

- **EmployeePublic**: Dados retornados
  - Todos os campos exceto `password_hash`

### AuditLog Schemas

- **AuditLogCreate**: Validação para criação
  - `employee_id`: UUID (opcional)
  - `company_id`: UUID (opcional)
  - `customer_wallet`: string (opcional)
  - `action_type`: min_length=1
  - `result`: min_length=1

- **AuditLogPublic**: Dados retornados
  - Todos os campos incluindo `timestamp`

---

## Configuração do Banco de Dados

### Conexão

O sistema utiliza SQLAlchemy com PostgreSQL:

```python
# Configuração baseada em variáveis de ambiente
DATABASE_URL = os.getenv("DATABASE_URL")

# Desenvolvimento local
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost/programacaoiii_db"

# Engine e Session
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

### Injeção de Dependência

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## Segurança

### Senhas

- Todas as senhas são armazenadas com hash usando bcrypt
- Nunca são retornadas nas respostas da API
- Validação de tamanho mínimo (8 caracteres)

### Chaves Primárias

- **Users e Roles**: INTEGER (auto-incremento)
- **Companies, Employees, AuditLogs**: UUID (universalmente único)

### Índices

Índices estratégicos para otimizar consultas:
- Emails (login rápido)
- Wallet addresses (acesso blockchain)
- Customer wallet (auditoria)
- Timestamps (ordenação temporal)

---

## Integração com Blockchain

### Wallet Addresses

- **Users**: Gerenciado no frontend (MetaMask)
- **Companies**: Armazenado em `companies.wallet_address`
- **Employees**: Usam o wallet da empresa

### Smart Contract

O banco de dados complementa a blockchain:
- **Blockchain**: Armazena consentimentos e dados sensíveis
- **Database**: Armazena informações de autenticação e auditoria

---

## Migrations e Manutenção

### Criação de Tabelas

```python
from database import Base, engine
from users.user_model import User
from companies.company_model import Company
from employees.employee_model import Employee
from roles.role_model import Role
from audit_logs.audit_log_model import AuditLog

# Criar todas as tabelas
Base.metadata.create_all(bind=engine)
```

### Extensibilidade

Todos os modelos usam `__table_args__ = {'extend_existing': True}` para permitir redefinições durante desenvolvimento.

---

## Considerações de Performance

### Índices Implementados

1. **Primary Keys**: Todas as tabelas
2. **Unique Constraints**: emails, wallet_address
3. **Foreign Keys**: Relacionamentos otimizados
4. **Custom Indexes**: full_name, cnpj, customer_wallet

### Otimizações

- Uso de UUIDs para distribuição de dados
- Timestamps com timezone para precisão
- Relacionamentos lazy-loading via SQLAlchemy
- Connection pooling via SessionLocal

---

## Backup e Recuperação

### Dados Críticos

1. **USERS**: Informações de autenticação
2. **COMPANIES**: Carteiras blockchain
3. **AUDIT_LOGS**: Rastreabilidade completa

### Estratégia Recomendada

- Backup diário do PostgreSQL
- Replicação para ambiente de staging
- Logs de auditoria imutáveis
- Sincronização com dados da blockchain

---

## Próximos Passos

### Melhorias Sugeridas

1. **Soft Delete**: Adicionar campo `deleted_at` para exclusão lógica
2. **Versionamento**: Histórico de alterações em dados sensíveis
3. **Criptografia**: Campos sensíveis criptografados no banco
4. **Particionamento**: Tabela de audit_logs por data
5. **Cache**: Redis para consultas frequentes

### Novos Recursos

1. **Notificações**: Tabela para alertas aos usuários
2. **Permissões Granulares**: Sistema de ACL mais detalhado
3. **Analytics**: Tabelas agregadas para dashboards
4. **Webhooks**: Registro de integrações externas

---

## Referências

- **Arquivos de Modelo**:
  - [user_model.py](file:///c:/Users/Administrador/Desktop/Blockchain/Projeto%20V2/Back/app/users/user_model.py)
  - [company_model.py](file:///c:/Users/Administrador/Desktop/Blockchain/Projeto%20V2/Back/app/companies/company_model.py)
  - [employee_model.py](file:///c:/Users/Administrador/Desktop/Blockchain/Projeto%20V2/Back/app/employees/employee_model.py)
  - [role_model.py](file:///c:/Users/Administrador/Desktop/Blockchain/Projeto%20V2/Back/app/roles/role_model.py)
  - [audit_log_model.py](file:///c:/Users/Administrador/Desktop/Blockchain/Projeto%20V2/Back/app/audit_logs/audit_log_model.py)
  - [database.py](file:///c:/Users/Administrador/Desktop/Blockchain/Projeto%20V2/Back/app/database.py)

- **Documentação**:
  - SQLAlchemy: https://docs.sqlalchemy.org/
  - Pydantic: https://docs.pydantic.dev/
  - PostgreSQL: https://www.postgresql.org/docs/
