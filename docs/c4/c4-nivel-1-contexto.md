# C4 — Nível 1: Contexto

> **Pergunta respondida:** O que é o sistema e quem o usa?

```mermaid
C4Context
  title Diagrama de Contexto — FundamentAI

  Person(iniciante, "Investidor Iniciante", "Busca entender ativos da B3 sem conhecimento técnico aprofundado")
  Person(intermediario, "Investidor Intermediário", "Analisa ações e FIIs com foco em indicadores e comparação setorial")
  Person(estudante, "Estudante de Finanças", "Usa a plataforma como ferramenta educativa sobre análise fundamentalista")

  System(fundamentai, "FundamentAI", "Plataforma web que consolida dados financeiros públicos, calcula indicadores fundamentalistas e gera análises via IA para ações e FIIs da B3")

  System_Ext(anthropic, "Anthropic API", "Geração de análises textuais estruturadas via modelos Claude (Sonnet e Haiku)")
  System_Ext(fundamentus, "fundamentus", "Indicadores fundamentalistas de ações da B3: P/L, ROE, Margem, EV/EBITDA, DY")
  System_Ext(yfinance, "yfinance", "Cotações, histórico de preços, DRE histórico de ações e dados completos de FIIs")
  System_Ext(bcb, "API Banco Central (BCB/SGS)", "Dados macroeconômicos: SELIC (série 11) e IPCA (série 433)")

  Rel(iniciante, fundamentai, "Consulta análise de ativos por ticker", "HTTPS")
  Rel(intermediario, fundamentai, "Consulta análise e comparação setorial", "HTTPS")
  Rel(estudante, fundamentai, "Consulta indicadores com explicações didáticas", "HTTPS")

  Rel(fundamentai, anthropic, "Envia prompt estruturado e recebe análise em JSON", "HTTPS")
  Rel(fundamentai, fundamentus, "Coleta indicadores fundamentalistas de ações", "HTTP / scraping")
  Rel(fundamentai, yfinance, "Coleta cotações, histórico DRE e dados de FIIs", "HTTPS")
  Rel(fundamentai, bcb, "Coleta SELIC e IPCA via API pública", "HTTPS")
```

---

## Elementos pendentes de implementação

Nenhum. Todos os sistemas externos e personas representados neste nível já estão integrados ou definidos no projeto.

---

## Revisão técnica

- **Decisões de design representadas:**
  - O sistema é apresentado como uma unidade coesa — detalhe interno omitido intencionalmente neste nível.
  - As três personas refletem os perfis definidos no `docs/PRD.md` (seção 1.3).
  - `fundamentus` e `yfinance` são fontes distintas com responsabilidades complementares: `fundamentus` cobre indicadores de ações; `yfinance` cobre FIIs (exclusivo) e histórico DRE de ações.
  - A API do BCB é representada como sistema externo independente, não agrupada com as demais fontes financeiras, pois fornece contexto macroeconômico — não dados de ativos.

- **Limitações deste diagrama:**
  - Não distingue os containers internos do FundamentAI (frontend, API, ETL, banco).
  - Não mostra frequência ou direção temporal das integrações (ex: ETL diário vs. consulta sob demanda).
  - O disclaimer de não-recomendação de investimento não é representável em C4 — pertence à documentação de produto.

- **O que será detalhado no Nível 2 (Container):**
  - Decomposição interna do FundamentAI em: Frontend React, API FastAPI, ETL Scheduler, banco de dados e módulo de prompts.
  - Protocolos e direção das comunicações entre os containers.
  - Identificação dos componentes do frontend ainda não implementados (marcados com `*`).
