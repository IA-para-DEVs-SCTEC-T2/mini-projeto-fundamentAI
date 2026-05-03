# Prompt Logs: feature/coletor-fundamentus

Histórico de prompts executados no Kiro nesta branch.

---

## Prompt: Implementar coletor fundamentus — issue #15
- Responsável: Michele Oliveira
- Branch: feature/coletor-fundamentus
- Data/hora: 2026-05-03 15:38:00 (Brasília)

### Prompt original
```
[Contexto: implementação do backend seguindo a ordem das issues do GitHub]

Issue #15 — feat(collectors): implementar coletor fundamentus para ações

Escopo:
- Criar backend/collectors/fundamentus.py
- Implementar função para coletar indicadores fundamentalistas (ROE, ROIC, P/L, P/VP,
  Margem Líquida, Dívida Líquida/EBITDA)
- Implementar função para identificar setor da empresa
- Tratar erros de API e tickers inválidos
- Normalizar dados para formato padrão do sistema

Critérios de Aceite:
- Função get_fundamentals(ticker) retorna todos os indicadores
- Função get_sector(ticker) retorna setor da empresa
- Tratamento de erros para tickers inválidos ou dados indisponíveis
- Dados normalizados em formato pandas DataFrame
- Documentação das funções com exemplos de uso
- Validação de que os dados são específicos de ações da B3
```

---
