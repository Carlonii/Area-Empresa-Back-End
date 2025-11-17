

"""
Testes Unitários

Este arquivo contém testes unitários para os endpoints de usuários da API.
Testes unitários são uma prática fundamental no desenvolvimento de software que visa
verificar o comportamento correto de unidades individuais de código, como funções,
métodos ou, neste caso, endpoints de API.

Aqui, utilizamos o TestClient do FastAPI para simular requisições HTTP aos endpoints,
permitindo testar a lógica de negócio, validações e respostas da API sem depender
de um servidor real em execução.

Os testes cobrem operações CRUD (Create, Read, Update, Delete) e validações de dados,
garantindo que a API funcione corretamente e retorne respostas adequadas.
"""

from fastapi.testclient import TestClient
from main import app
import pytest

# Credenciais para login no sistema
# Estas credenciais são usadas para obter um token JWT válido,
# necessário para acessar endpoints protegidos pela autenticação
LOGIN_EMAIL = "murilo.assis@ifg.edu.br"
LOGIN_PASSWORD = "12345678"

# Fixture para criar o client e obter o token JWT antes dos testes
# Esta fixture é executada uma vez por módulo de teste e fornece
# um cliente HTTP configurado e um token de autenticação válido
@pytest.fixture(scope="module")
def client_and_token():
    client = TestClient(app)
    # Realiza login via API para obter token de acesso
    login_response = client.post("/auth/login", data={
        "username": LOGIN_EMAIL,
        "password": LOGIN_PASSWORD
    })
    assert login_response.status_code == 200, f"Login falhou: {login_response.text}"
    token = login_response.json()["access_token"]
    return client, token

def test_user_crud_sequence(client_and_token):
    """
    Testa a sequência completa de operações CRUD para usuários.
    
    Este teste verifica se é possível criar, alterar e excluir um usuário
    através da API, validando que cada operação retorna o status correto
    e os dados esperados. Também testa a integridade dos relacionamentos
    (como a vinculação com roles).
    """
    client, token = client_and_token
    headers = {"Authorization": f"Bearer {token}"}

    # Gerar sufixo aleatório para e-mail do usuário de teste
    # Isso evita conflitos de duplicidade de e-mail entre execuções de teste
    import random, string
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    test_email = f"test_sequence_user_{random_suffix}@example.com"

    # Buscar uma role existente para vincular ao usuário
    # Garante que sempre haverá uma role válida para o teste,
    # evitando dependências externas ou falhas por falta de dados
    roles_resp = client.get("/roles/", headers=headers)
    assert roles_resp.status_code == 200 and len(roles_resp.json()) > 0, "Nenhuma role disponível para vincular ao usuário."
    role_id = roles_resp.json()[0]["id"]

    # 1. Criar usuário
    # Testa a criação de um novo usuário com dados válidos
    user_data = {
        "email": test_email,
        "password": "password123",
        "full_name": "Test Sequence User",
        "role_id": role_id
    }
    # Chama o endpoint de criação de usuário
    user_resp = client.post("/users/", json=user_data, headers=headers)
    assert user_resp.status_code == 201, f"Falha ao criar usuário: {user_resp.text}"
    user_id = user_resp.json()["id"]
    user_json = user_resp.json()
    # Valida que os dados retornados correspondem aos enviados
    assert user_json["email"] == test_email
    assert user_json["full_name"] == "Test Sequence User"
    assert "role" in user_json and user_json["role"]["id"] == role_id

    # 2. Alterar usuário
    # Testa a atualização de dados do usuário criado
    update_user_data = {
        "full_name": "Test Sequence User Updated",
        "role_id": role_id
    }
    # Chama o endpoint de atualização de usuário
    update_user_resp = client.put(f"/users/{user_id}", json=update_user_data, headers=headers)
    assert update_user_resp.status_code == 200, f"Falha ao atualizar usuário: {update_user_resp.text}"
    update_json = update_user_resp.json()
    # Valida que o nome foi atualizado, mas o e-mail permanece o mesmo
    assert update_json["email"] == test_email
    assert update_json["full_name"] == "Test Sequence User Updated"
    assert "role" in update_json and update_json["role"]["id"] == role_id

    # 3. Excluir usuário
    # Testa a exclusão do usuário criado
    # Chama o endpoint de exclusão de usuário
    delete_user_resp = client.delete(f"/users/{user_id}", headers=headers)
    assert delete_user_resp.status_code == 200, f"Falha ao excluir usuário: {delete_user_resp.text}"
    deleted_json = delete_user_resp.json()
    # Valida que os dados retornados correspondem ao usuário excluído
    assert deleted_json["id"] == user_id
    assert deleted_json["email"] == test_email
    assert deleted_json["full_name"] == "Test Sequence User Updated"
    assert "role" in deleted_json and deleted_json["role"]["id"] == role_id