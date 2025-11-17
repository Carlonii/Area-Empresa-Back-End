from fastapi.testclient import TestClient
from main import app
import pytest

# Credenciais para login no sistema
LOGIN_EMAIL = "murilo.assis@ifg.edu.br"
LOGIN_PASSWORD = "12345678"

# Fixture para criar o client e obter o token JWT antes dos testes
@pytest.fixture(scope="module")
def client_and_token():
    client = TestClient(app)
    # Realiza login via API
    login_response = client.post("/auth/login", data={
        "username": LOGIN_EMAIL,
        "password": LOGIN_PASSWORD
    })
    assert login_response.status_code == 200, f"Login falhou: {login_response.text}"
    token = login_response.json()["access_token"]
    return client, token


def test_role_crud_sequence(client_and_token):
    """
    Testa a sequência completa de operações CRUD para roles.
    
    Verifica se é possível criar, alterar e excluir uma role através da API,
    validando status codes e dados retornados. Usa nomes aleatórios para
    evitar conflitos entre execuções de teste.
    """
    client, token = client_and_token
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Criar uma role nova
    import random, string
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    role_name = f"test_role_sequence_{random_suffix}"
    role_data = {"name": role_name}
    role_resp = client.post("/roles/", json=role_data, headers=headers)
    assert role_resp.status_code == 201, f"Falha ao criar role: {role_resp.text}"
    role_id = role_resp.json()["id"]
    assert role_resp.json()["name"] == role_name

    # 2. Alterar a role criada
    update_role_data = {"name": f"test_role_sequence_updated_{random_suffix}"}
    update_role_resp = client.put(f"/roles/{role_id}", json=update_role_data, headers=headers)
    assert update_role_resp.status_code == 200, f"Falha ao atualizar role: {update_role_resp.text}"
    assert update_role_resp.json()["name"] == f"test_role_sequence_updated_{random_suffix}"

    # 3. Excluir a role criada
    delete_role_resp = client.delete(f"/roles/{role_id}", headers=headers)
    assert delete_role_resp.status_code == 200, f"Falha ao excluir role: {delete_role_resp.text}"
    deleted_role_json = delete_role_resp.json()
    assert deleted_role_json["id"] == role_id
    assert deleted_role_json["name"] == f"test_role_sequence_updated_{random_suffix}"


def test_role_nome_ausente(client_and_token):
    """
    Testa criação de role sem nome (campo obrigatório).
    
    Verifica se a API rejeita corretamente a criação quando o campo
    obrigatório 'name' não é fornecido, retornando erro de validação.
    """
    client, token = client_and_token
    headers = {"Authorization": f"Bearer {token}"}
    role_data = {}
    resp = client.post("/roles/", json=role_data, headers=headers)
    assert resp.status_code == 422, f"Role criada sem nome: {resp.text}"

def test_role_nome_duplicado(client_and_token):
    """
    Testa criação de role com nome duplicado.
    
    Cria uma role, tenta criar outra com o mesmo nome e verifica
    se a API impede a duplicidade. Limpa os dados após o teste.
    """
    client, token = client_and_token
    headers = {"Authorization": f"Bearer {token}"}
    role_name = "role_duplicada_teste"
    role_data = {"name": role_name}
    # Cria a primeira role
    resp1 = client.post("/roles/", json=role_data, headers=headers)
    assert resp1.status_code == 201
    # Tenta criar novamente
    resp2 = client.post("/roles/", json=role_data, headers=headers)
    assert resp2.status_code == 400 or resp2.status_code == 409, f"Role duplicada criada: {resp2.text}"
    # Limpa a role criada
    role_id = resp1.json()["id"]
    client.delete(f"/roles/{role_id}", headers=headers)

def test_role_nome_curto(client_and_token):
    """
    Testa criação de role com nome muito curto.
    
    Verifica se a API rejeita nomes com menos de 3 caracteres,
    conforme validação definida no modelo Pydantic.
    """
    client, token = client_and_token
    headers = {"Authorization": f"Bearer {token}"}
    role_data = {"name": "a"}
    resp = client.post("/roles/", json=role_data, headers=headers)
    assert resp.status_code == 422 or resp.status_code == 400, f"Role criada com nome curto: {resp.text}"
