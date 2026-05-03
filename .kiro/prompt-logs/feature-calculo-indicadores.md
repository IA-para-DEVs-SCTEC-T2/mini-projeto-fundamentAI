# Prompt Logs: feature/calculo-indicadores

Histórico de prompts executados no Kiro nesta branch.

---

## Prompt: Implementar cálculo de indicadores fundamentalistas — issue #17
- Responsável: Michele Oliveira
- Branch: feature/calculo-indicadores
- Data/hora: 2026-05-03 15:50:00 (Brasília)

### Prompt original
```
[Contexto: implementação do backend seguindo a ordem das issues do GitHub]

Issue #17 — feat(processors): implementar cálculo de indicadores

Escopo:
- Criar backend/processors/indicators.py
- Implementar cálculo de ROE (Retorno sobre Patrimônio)
- Implementar cálculo de ROIC (Retorno sobre Capital Investido)
- Implementar cálculo de Margem Líquida
- Implementar cálculo de Dívida Líquida / EBITDA
- Implementar cálculo de P/L (Preço / Lucro)
- Implementar cálculo de P/VP (Preço / Valor Patrimonial)
- Validar dados de entrada e tratar casos especiais (divisão por zero, dados ausentes)

Critérios de Aceite:
- Função calculate_roe(data) retorna ROE calculado corretamente
- Função calculate_roic(data) retorna ROIC calculado corretamente
- Função calculate_net_margin(data) retorna margem líquida
- Função calculate_debt_ebitda(data) retorna dívida líquida/EBITDA
- Função calculate_pe_ratio(data) retorna P/L
- Função calculate_pb_ratio(data) retorna P/VP
- Tratamento de casos especiais (divisão por zero, dados ausentes)
- Testes unitários para cada indicador
```

---
