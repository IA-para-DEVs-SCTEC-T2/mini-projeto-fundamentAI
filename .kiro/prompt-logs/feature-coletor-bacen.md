# Prompt Logs: feature/coletor-bacen

Histórico de prompts executados no Kiro nesta branch.

---

## Prompt: Implementar coletor API Banco Central — issue #16
- Responsável: Michele Oliveira
- Branch: feature/coletor-bacen
- Data/hora: 2026-05-03 15:44:00 (Brasília)

### Prompt original
```
[Contexto: implementação do backend seguindo a ordem das issues do GitHub]

Issue #16 — feat(collectors): implementar coletor API Banco Central

Escopo:
- Criar backend/collectors/bacen.py
- Implementar função para coletar taxa SELIC atual e histórica
- Implementar função para coletar IPCA atual e histórico
- Implementar cache para evitar chamadas desnecessárias (dados macro mudam com menor frequência)
- Tratar erros de API e timeouts
- Normalizar dados para formato padrão do sistema

Critérios de Aceite:
- Função get_selic() retorna taxa SELIC atual
- Função get_ipca() retorna IPCA atual
- Funções com parâmetro opcional para histórico (últimos 12 meses)
- Cache implementado para reduzir chamadas à API
- Tratamento de erros e timeouts
- Documentação das funções com exemplos de uso
```

---
