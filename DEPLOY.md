# Guia de Deploy no Render

## Instruções para Deploy

### 1. Preparação do Projeto

O projeto está configurado para usar a variável de ambiente `APP_PROFILE` para distinguir entre desenvolvimento e produção:

- **DEV**: Usa PostgreSQL local, CORS permissivo, cria tabelas automaticamente
- **PROD**: Usa DATABASE_URL do Render, CORS restritivo, não cria tabelas (use migrações)

### 2. Arquivos de Deploy Criados

- `Dockerfile`: Container para produção com Python 3.11 e Poetry
- `.dockerignore`: Exclui arquivos desnecessários do container
- `render.yaml`: Configuração Blueprint do Render (opcional)

### 3. Deploy Manual no Render

1. **Conecte seu repositório GitHub ao Render**
2. **Crie um novo Web Service**
3. **Configure as variáveis de ambiente:**
   - `APP_PROFILE=PROD`
   - `DATABASE_URL` (será fornecida automaticamente pelo banco PostgreSQL)
4. **Configure o banco de dados PostgreSQL no Render**
5. **Deploy será feito automaticamente**

### 4. Deploy usando Blueprint (render.yaml)

1. **Conecte seu repositório ao Render**
2. **Selecione "Blueprint"**
3. **O arquivo render.yaml será usado automaticamente**
4. **Confirme a criação dos recursos**

### 5. Configurações Importantes

#### Variáveis de Ambiente no Render:
```
APP_PROFILE=PROD
DATABASE_URL=<fornecida_automaticamente_pelo_render>
```

#### CORS em Produção:
- Por padrão, está configurado para `https://yourdomain.com`
- **IMPORTANTE**: Altere no `main.py` linha 29 para seu domínio real

### 6. Após o Deploy

1. **Acesse sua aplicação em**: `https://seu-app.onrender.com`
2. **Documentação da API**: `https://seu-app.onrender.com/docs`
3. **Crie as tabelas do banco** (se necessário, via endpoint ou script)

### 7. Comandos Úteis para Testes Locais

```bash
# Testar o container localmente
docker build -t programacaoiii-api .
docker run -p 8000:8000 -e APP_PROFILE=PROD programacaoiii-api

# Testar em modo desenvolvimento
poetry install
poetry run python app/main.py
```

### 8. Troubleshooting

- **Erro de CORS**: Ajuste os domínios permitidos no `main.py`
- **Erro de banco**: Verifique se o PostgreSQL está configurado no Render
- **Erro de dependências**: Verifique se o `pyproject.toml` está correto
- **Erro de build**: Verifique os logs do Docker no Render

### 9. Próximos Passos Recomendados

1. Implementar migrações de banco com Alembic
2. Adicionar health check endpoint
3. Configurar logs estruturados
4. Implementar monitoramento
5. Configurar CI/CD com GitHub Actions