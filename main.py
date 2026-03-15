import os
import sys
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Adiciona a pasta app ao Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Importa logger e funcoes de resposta padrao
from utils.response import get_logger, error_response

logger = get_logger("fastapi_app")

# Importa primeiro a base e engine para evitar problemas de ordem
from database import engine, Base

# Depois importa os controllers
from auth import auth_controller
# Importa modelos adicionais para garantir que as tabelas sejam registradas
from companies import company_model
from employees import employee_model
from audit_logs import audit_log_model
from companies import company_api_key_model, company_webhook_model, data_usage_model
from notifications import notification_model

# Importa novos controllers
from users import user_controller
from roles import role_controller
from companies import company_controller
from employees import employee_controller
from auth import employee_auth_controller
from data import data_controller
from audit_logs import audit_controller
from health import health_controller
from notifications import notification_controller
from config import settings

# Importa modelos para registro na base
from utils import config_model

# Criar tabelas apenas em desenvolvimento
if settings.APP_PROFILE == "DEV":
    Base.metadata.create_all(bind=engine)

# 1. Cria a instancia principal da aplicacao
app = FastAPI(
    title="API do Meu Projeto",
    version="0.1.0"
)

# Exception handlers globais
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"HTTP Exception: {exc.detail} no endpoint {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(message=str(exc.detail))
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation Error: {exc.errors()} no endpoint {request.url.path}")
    return JSONResponse(
        status_code=422,
        content=error_response(message="Erro de validação dos dados enviados.", data=exc.errors())
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro interno no servidor: {str(exc)} no endpoint {request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=error_response(message="Ocorreu um erro interno no servidor.")
    )

# Configuracao de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS if settings.APP_PROFILE != "DEV" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Inclui o roteador de usuarios na aplicacao principal
app.include_router(user_controller.router)
app.include_router(role_controller.router)
app.include_router(auth_controller.router)
app.include_router(company_controller.router)
app.include_router(employee_controller.router)
app.include_router(employee_auth_controller.router)
app.include_router(data_controller.router)
app.include_router(audit_controller.router)
app.include_router(health_controller.router)
app.include_router(notification_controller.router)

# 4. Codigo para rodar o servidor
if __name__ == '__main__':
    # Este bloco so executa quando rodamos o script diretamente (python main.py)
    uvicorn.run(app, host="0.0.0.0", port=8000)
