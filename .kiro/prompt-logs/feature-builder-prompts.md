# Prompt Logs: feature/builder-prompts

Histórico de prompts executados no Kiro nesta branch.

---

## Prompt: Implementar builder de prompts estruturados — issue #20
- Responsável: Michele Oliveira
- Branch: feature/builder-prompts
- Data/hora: 2026-05-03 16:08:00 (Brasília)

### Prompt original
```
[Contexto: implementação do backend seguindo a ordem das issues do GitHub]

Issue #20 — feat(prompts): implementar builder de prompts estruturados

Escopo:
- Criar backend/prompts/builder.py
- Implementar template de prompt estruturado
- Implementar função para injetar dados financeiros no template
- Implementar função para injetar indicadores calculados
- Implementar função para injetar contexto macroeconômico (SELIC, IPCA)
- Definir formato de saída esperado (JSON estruturado)
- Versionar templates de prompt

Critérios de Aceite:
- Função build_analysis_prompt(ticker, data, indicators, macro) retorna prompt completo
- Template separado da lógica de injeção de dados
- Formato de saída JSON estruturado definido no prompt
- Prompt inclui: dados financeiros, indicadores, contexto macro, critérios de análise
- Templates versionados (não hardcoded)
- Documentação do formato de entrada e saída
```

---
