# C4 — Nível 2: Container

> **Pergunta respondida:** Como o sistema está dividido tecnicamente?

```mermaid
C4Container
  title Diagrama de Container — FundamentAI

  Person(usuario, "Usuário (Investidor / Estudante)", "Acessa a plataforma via navegador para consultar análises de ações e FIIs")

  System_Boundary(fundamentai, "FundamentAI") {

    Container(frontend, "Frontend React [*]", "React, Vite, Axios", "SPA para busca por ticker e exibição do dashboard de análise. Parcialmente implementado — ver elementos pendentes.")

    Container(api, "API REST", "FastAPI, Python 3.12, Uvicorn (porta 8000)", "Expõe os endpoints GET /api/ticker/{ticker} e POST /api/analysis/{ticker}. Orquestra classificação, scoring, comparação setorial, construção de prompt e chamada à LLM.")

    Container(etl, "ETL Scheduler", "Python, APScheduler", "Pipeline diário disparado às 19h (fuso Brasília). Coleta dados nas fontes externas, processa indicadores e persiste no banco. Executa ensure_min_indicators ao final.")

    ContainerDb(db, "Banco de Dados", "SQLite (dev) / PostgreSQL (prod) via SQLAlchemy", "Armazena tickers ativos, tickers inativos, dados financeiros brutos, indicadores calculados e análises geradas pela LLM.")
  }

  System_Ext(anthropic, "Anthropic API", "Geração de análises textuais estruturadas via Claude Sonnet 4.5 e Haiku 4.5")
  System_Ext(fundamentus, "fundamentus", "Indicadores fundamentalistas de ações da B3: P/L, ROE, Margem, EV/EBITDA, DY")
  System_Ext(yfinance, "yfinance", "Cotações, histórico de preços, DRE histórico de ações e todos os dados de FIIs")
  System_Ext(bcb, "API Banco Central (BCB/SGS)", "Dados macroeconômicos: SELIC (série 11) e IPCA (série 433)")

  Rel(usuario, frontend, "Digita ticker e visualiza análise", "HTTPS")
  Rel(frontend, api, "Consulta dados do ticker e solicita análise", "HTTP REST / JSON")
  Rel(api, db, "Lê indicadores, tickers e análises; persiste resultados", "SQL via SQLAlchemy")
  Rel(api, anthropic, "Envia prompt estruturado e recebe análise em JSON", "HTTPS")
  Rel(etl, fundamentus, "Coleta indicadores fundamentalistas de ações", "HTTP / scraping")
  Rel(etl, yfinance, "Coleta cotações, histórico DRE e dados completos de FIIs", "HTTPS")
  Rel(etl, bcb, "Coleta SELIC e IPCA via API pública", "HTTPS")
  Rel(etl, db, "Persiste dados financeiros brutos e indicadores calculados", "SQL via SQLAlchemy")
```

---

## Elementos pendentes de implementação

Os itens marcados com `*` ainda não existem no repositório e precisam ser criados.

| Elemento | Localização esperada | Descrição |
|---|---|---|
| `Home [*]` | `frontend/src/pages/Home/` | Página inicial com campo de busca por ticker — ponto de entrada da aplicação |
| `ScoreCard [*]` | `frontend/src/components/ScoreCard/` | Componente de exibição do score (0–100) e classificação qualitativa (Excelente / Bom / Regular / Fraco) |
| `IndicatorTable [*]` | `frontend/src/components/IndicatorTable/` | Tabela de indicadores fundamentalistas com tooltips explicativos por tipo de ativo |
| `Chart [*]` | `frontend/src/components/Chart/` | Gráficos de histórico de preços, evolução de indicadores e comparação setorial |
| `Verdict [*]` | `frontend/src/components/Verdict/` | Componente de exibição do veredito, pontos positivos/negativos e conclusão gerados pela IA |
| `hooks/ [*]` | `frontend/src/hooks/` | Custom hooks React para encapsular lógica de busca, estado e formatação |
| `utils/ [*]` | `frontend/src/utils/` | Funções auxiliares de formatação de números, datas e tratamento de erros da API |

> O container **Frontend React** existe e está funcional como scaffold (`App.jsx`, `Analysis.jsx`, `services/api.js`), mas depende da criação dos itens acima para atender os requisitos funcionais definidos no PRD.

---

## Revisão técnica

- **Decisões de design representadas:**
  - O **ETL Scheduler** é um container independente da API — não compartilha processo com o FastAPI. Isso permite escalar e reiniciar cada um separadamente.
  - A **API REST** é stateless: todo o estado persiste no banco via SQLAlchemy, o que viabiliza escalabilidade horizontal futura.
  - O **Banco de Dados** é representado como container único com dois modos (SQLite/PostgreSQL) — a abstração SQLAlchemy garante que nenhum SQL vendor-specific existe no código da aplicação.
  - A chamada à **Anthropic API** parte exclusivamente da API REST (sob demanda), nunca do ETL — o ETL apenas coleta e processa dados financeiros.
  - O **Frontend** se comunica apenas com a API REST, nunca diretamente com fontes externas ou banco — arquitetura de separação de responsabilidades preservada.

- **Limitações deste diagrama:**
  - O módulo `backend/prompts/builder.py` não aparece como container separado — é um componente interno da API REST, detalhado no Nível 3.
  - O `ensure_min_indicators` e demais scripts de manutenção são subprocessos do ETL, não containers independentes.
  - Não representa autenticação de usuário — fora do escopo do MVP conforme PRD.

- **O que será detalhado no Nível 3 (Componente):**
  - Decomposição interna do container **API REST** em seus componentes: rotas, processors (`asset_classifier`, `indicators`, `scoring`, `comparator`), `db/repository` e `prompts/builder`.
  - Identificação de quaisquer componentes previstos na arquitetura mas ainda ausentes no código.
