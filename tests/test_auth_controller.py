"""
Testes Unitários para Autenticação

Este arquivo contém testes unitários para os endpoints de autenticação da API.
Testes unitários são uma prática fundamental no desenvolvimento de software que visa
verificar o comportamento correto de unidades individuais de código, como funções,
métodos ou, neste caso, endpoints de API.

Aqui, utilizamos o TestClient do FastAPI para simular requisições HTTP aos endpoints,
permitindo testar a lógica de negócio, validações e respostas da API sem depender
de um servidor real em execução.

Os testes cobrem cenários de autenticação e autorização, garantindo que a API
funcione corretamente e retorne respostas adequadas.
"""

from fastapi.testclient import TestClient
from main import app
import pytest

# Testes de autenticação e autorização
# Valida login, acesso negado sem token, e token inválido

LOGIN_EMAIL = "murilo.assis@ifg.edu.br"
LOGIN_PASSWORD = "12345678"

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_login_sucesso(client):
    """
    Testa login com credenciais válidas.
    
    Verifica se o endpoint de login aceita credenciais corretas
    e retorna um token de acesso JWT válido.
    """
    response = client.post("/auth/login", data={
        "username": LOGIN_EMAIL,
        "password": LOGIN_PASSWORD
    })
    assert response.status_code == 200, f"Login falhou: {response.text}"
    assert "access_token" in response.json()


def test_login_invalido(client):
    """
    Testa login com credenciais inválidas.
    
    Verifica se o endpoint de login rejeita credenciais incorretas
    e não retorna token de acesso.
    """
    response = client.post("/auth/login", data={
        "username": "usuario_invalido@ifg.edu.br",
        "password": "senhaerrada"
    })
    assert response.status_code == 401
    assert "access_token" not in response.json()


def test_acesso_sem_token(client):
    """
    Testa acesso negado a endpoint protegido sem token.
    
    Verifica se endpoints que requerem autenticação rejeitam
    requisições sem token de autorização.
    """
    response = client.get("/users/")
    assert response.status_code == 401 or response.status_code == 403


def test_acesso_com_token_invalido(client):
    """
    Testa acesso negado a endpoint protegido com token inválido.
    
    Verifica se endpoints que requerem autenticação rejeitam
    requisições com token malformado ou expirado.
    """
    headers = {"Authorization": "Bearer token_invalido"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 401 or response.status_code == 403
