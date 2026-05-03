# Prompt Logs: feature/comparacao-setorial

Histórico de prompts executados no Kiro nesta branch.

---

## Prompt: Implementar comparação setorial — issue #19
- Responsável: Michele Oliveira
- Branch: feature/comparacao-setorial
- Data/hora: 2026-05-03 16:02:00 (Brasília)

### Prompt original
```
[Contexto: implementação do backend seguindo a ordem das issues do GitHub]

Issue #19 — feat(processors): implementar comparação setorial

Escopo:
- Criar backend/processors/comparator.py
- Implementar função para identificar empresas do mesmo setor
- Implementar cálculo de médias setoriais dos indicadores
- Implementar comparação do ativo com a média do setor
- Incluir análise de negócio para definir como classificar setores (B3, yfinance, fundamentus)
- Gerar relatório de posicionamento relativo

Critérios de Aceite:
- Função get_sector_companies(sector) retorna empresas do setor
- Função calculate_sector_averages(sector) retorna médias setoriais
- Função compare_to_sector(ticker, indicators) retorna comparação
- Classificação setorial definida e documentada
- Relatório mostra se o ativo está acima/abaixo da média setorial
- Tratamento de setores com poucos dados
```

---
