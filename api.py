"""
API simples com FastAPI - CRUD de itens em memória.

Endpoints:
  GET    /items        → lista todos os itens
  POST   /items        → cria um novo item
  DELETE /items/{id}   → remove item pelo id (404 se não existir)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Items API")

# Banco de dados mockado em memória
items_db: list[dict] = [
    {"id": 1, "name": "Item A", "description": "Primeiro item"},
    {"id": 2, "name": "Item B", "description": "Segundo item"},
]

_next_id = 3  # contador simples de IDs


class ItemIn(BaseModel):
    name: str
    description: str = ""


# ---------------------------------------------------------------------------
# GET /items
# Retorna todos os itens da lista.
#
# Exemplo de resposta:
#   [{"id": 1, "name": "Item A", "description": "Primeiro item"}, ...]
# ---------------------------------------------------------------------------
@app.get("/items", status_code=200)
def list_items():
    print(f"[GET /items] Retornando {len(items_db)} itens")
    return items_db


# ---------------------------------------------------------------------------
# POST /items
# Recebe um item no corpo e o adiciona à lista.
#
# Exemplo de requisição:
#   {"name": "Item C", "description": "Terceiro item"}
#
# Exemplo de resposta (201):
#   {"id": 3, "name": "Item C", "description": "Terceiro item"}
# ---------------------------------------------------------------------------
@app.post("/items", status_code=201)
def create_item(item: ItemIn):
    global _next_id
    new_item = {"id": _next_id, "name": item.name, "description": item.description}
    items_db.append(new_item)
    _next_id += 1
    print(f"[POST /items] Item criado: {new_item}")
    return new_item


# ---------------------------------------------------------------------------
# DELETE /items/{id}
# Remove o item com o id informado.
# Retorna 404 se o id não existir.
#
# Exemplo de resposta (200):
#   {"detail": "Item 1 removido com sucesso"}
#
# Exemplo de resposta (404):
#   {"detail": "Item com id 99 não encontrado"}
# ---------------------------------------------------------------------------
@app.delete("/items/{item_id}", status_code=200)
def delete_item(item_id: int):
    for i, item in enumerate(items_db):
        if item["id"] == item_id:
            items_db.pop(i)
            print(f"[DELETE /items/{item_id}] Item removido")
            return {"detail": f"Item {item_id} removido com sucesso"}

    print(f"[DELETE /items/{item_id}] Item não encontrado")
    raise HTTPException(status_code=404, detail=f"Item com id {item_id} não encontrado")
