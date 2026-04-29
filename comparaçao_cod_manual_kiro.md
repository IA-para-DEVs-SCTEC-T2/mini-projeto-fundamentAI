# Comparação: `main.py` (manual) vs `main-kiro.py` (Kiro)

## Legibilidade

| | `main.py` | `main-kiro.py` |
|---|---|---|
| Nome da função | `analisar_lista` — genérico | `verificar_duplicados` — descreve exatamente o que faz |
| Nome das variáveis | `lista_sem_duplicados` — longo | `lista_limpa` — mais curto e direto |
| Espaçamento na lista | `[1,2,3,4...]` — sem espaços | `[1, 2, 3, 4...]` — segue PEP 8 |
| Print dos duplicados | Tudo em uma linha | Separado em duas linhas, mais claro |

**Vantagem: `main-kiro.py`**

---

## Eficiência

`main.py` usa `list` para `duplicados`:
```python
duplicados = []
if numero not in duplicados:  # O(n) — percorre a lista inteira
    duplicados.append(numero)
```

`main-kiro.py` usa `set` para `duplicados`:
```python
duplicados = set()
duplicados.add(numero)  # O(1) — busca em set é constante
```

Com listas grandes, a diferença é significativa.

**Vantagem: `main-kiro.py`**

---

## Edge Cases

`main.py` não cobre:
- Lista vazia → `lista_sem_duplicados` seria `[]` mas não avisa o usuário
- Todos duplicados → funciona, mas o print fica confuso
- `sorted()` não é usado → duplicados aparecem na ordem de encontro

`main-kiro.py` cobre melhor:
- `sorted(duplicados)` → exibe os duplicados em ordem crescente, mais legível
- Mesma limitação com lista vazia, mas o comportamento é mais previsível

**Vantagem: `main-kiro.py` (levemente)**

---

## Resumo

`main-kiro.py` ganha nas três categorias, principalmente em eficiência pelo uso de `set` para rastrear duplicados. O `main.py` tem a mesma lógica central, mas com escolhas menos otimizadas — o que é completamente normal para código escrito na mão sem referência.
