"""
Testes unitários para a API de itens usando pytest + httpx (TestClient do FastAPI).
"""

import pytest
from fastapi.testclient import TestClient
import api  # importa o módulo para poder resetar o estado entre testes


@pytest.fixture(autouse=True)
def reset_db():
    """Restaura o banco mockado e o contador de IDs antes de cada teste."""
    api.items_db.clear()
    api.items_db.extend([
        {"id": 1, "name": "Item A", "description": "Primeiro item"},
        {"id": 2, "name": "Item B", "description": "Segundo item"},
    ])
    api._next_id = 3


client = TestClient(api.app)


# ---------------------------------------------------------------------------
# Testes GET /items
# ---------------------------------------------------------------------------
def test_get_items_retorna_lista():
    response = client.get("/items")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["name"] == "Item A"


# ---------------------------------------------------------------------------
# Testes POST /items
# ---------------------------------------------------------------------------
def test_post_item_cria_com_sucesso():
    payload = {"name": "Item C", "description": "Terceiro item"}
    response = client.post("/items", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 3
    assert data["name"] == "Item C"
    assert data["description"] == "Terceiro item"


def test_post_item_aparece_na_lista():
    client.post("/items", json={"name": "Item C", "description": ""})
    response = client.get("/items")
    assert len(response.json()) == 3


# ---------------------------------------------------------------------------
# Testes DELETE /items/{id}
# ---------------------------------------------------------------------------
def test_delete_item_existente():
    response = client.delete("/items/1")
    assert response.status_code == 200
    assert "removido" in response.json()["detail"]
    # confirma que saiu da lista
    ids = [i["id"] for i in client.get("/items").json()]
    assert 1 not in ids


def test_delete_item_inexistente_retorna_404():
    response = client.delete("/items/99")
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"]
