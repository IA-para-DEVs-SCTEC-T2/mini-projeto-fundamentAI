# C4 — Nível 4: Código

> **Pergunta respondida:** Como o código está estruturado na camada de persistência?

```mermaid
classDiagram
  direction TB

  class Ticker {
    +Integer id PK
    +String symbol
    +String name
    +String sector
    +String segment
    +String asset_type
    +String b3_type
    +DateTime created_at
    +DateTime updated_at
  }

  class InactiveTicker {
    +Integer id PK
    +String symbol
    +String name
    +String sector
    +String asset_type
    +String b3_type
    +String reason
    +Float last_price
    +DateTime last_checked_at
    +DateTime created_at
  }

  class FinancialData {
    +Integer id PK
    +Integer ticker_id FK
    +DateTime reference_date
    +Float current_price
    +Float market_cap
    %% -- Ações --
    +Float revenue
    +Float net_income
    +Float ebitda
    +Float gross_profit
    +Float total_assets
    +Float total_equity
    +Float total_debt
    +Float net_debt
    +Float invested_capital
    +Float enterprise_value
    %% -- FIIs --
    +Float book_value_per_share
    +Float shares_outstanding
    +Float dividend_yield
    +Float last_dividend
    +DateTime last_dividend_date
    +Float dividends_12m
    +Float dividend_growth_yoy
    +Text raw_data
    +DateTime collected_at
  }

  class Indicators {
    +Integer id PK
    +Integer ticker_id FK
    +DateTime reference_date
    %% -- Ações --
    +Float roe
    +Float roic
    +Float net_margin
    +Float debt_ebitda
    +Float ev_ebitda
    +Float net_income_growth_yoy
    +Float revenue_growth_yoy
    %% -- Comuns (ações e FIIs) --
    +Float pe_ratio
    +Float pb_ratio
    +Float dividend_yield
    %% -- FIIs --
    +Float dividend_growth_yoy
    %% -- Score unificado --
    +Float score
    +String score_label
    +DateTime calculated_at
  }

  class Analysis {
    +Integer id PK
    +Integer ticker_id FK
    +String verdict
    +Float score
    +String confidence_level
    +Text positive_points
    +Text negative_points
    +Text indicators_explanation
    +Text conclusion
    +Text moment_suggestion
    +String model_used
    +String prompt_version
    +Text raw_response
    +String risk_assessment*
    +DateTime generated_at
  }

  Ticker "1" --> "0..*" FinancialData : financial_data
  Ticker "1" --> "0..*" Indicators : indicators
  Ticker "1" --> "0..*" Analysis : analyses
```

> `*` Atributo previsto no PRD e no schema de resposta da API (`AnalysisResponse`), mas **ainda não implementado** na tabela `analyses` do banco de dados — ver elementos pendentes abaixo.

---

## Elementos pendentes de implementação

| Elemento | Localização esperada | Descrição |
|---|---|---|
| `risk_assessment*` | `Analysis.risk_assessment` — coluna `String` em `backend/db/models.py` | Campo presente no `AnalysisResponse` (Pydantic) e retornado pela API, mas não persistido na tabela `analyses`. A avaliação de risco gerada pela LLM é descartada após cada requisição — não fica disponível para consultas históricas. |

---

## Revisão técnica

- **Decisões de design representadas:**
  - `Ticker` é a entidade central: `FinancialData`, `Indicators` e `Analysis` são dependentes e possuem cascade `all, delete-orphan` — excluir um `Ticker` remove todos os seus dados associados.
  - `InactiveTicker` é uma entidade independente, sem relacionamento com `Ticker` — garante que um ticker inativo nunca coexista com um ticker ativo no sistema.
  - `FinancialData` e `Indicators` possuem campos separados por tipo de ativo (`ações` vs `FIIs`), mas estão na mesma tabela — design intencional para manter o output unificado e simplificar o ORM.
  - O campo `raw_data` em `FinancialData` (JSON/Text) oferece flexibilidade para preservar dados brutos sem exigir migrations imediatas ao adicionar novas fontes.
  - `Analysis` armazena `positive_points`, `negative_points` e `indicators_explanation` como `Text` (JSON serializado) — evita tabelas auxiliares para listas, ao custo de não permitir queries SQL nesses campos.
  - O campo `score` existe tanto em `Indicators` (calculado localmente pelos processors) quanto em `Analysis` (retornado pela LLM) — os dois podem divergir e são tratados como fontes independentes.

- **Limitações deste diagrama:**
  - Não representa índices de banco (`index=True`) nem restrições de unicidade (`unique=True`) — detalhes relevantes para performance em produção (PostgreSQL).
  - O campo `reference_date` em `FinancialData` e `Indicators` funciona como chave de série temporal — o diagrama não representa a constraint de unicidade composta `(ticker_id, reference_date)`.
  - Não cobre as funções auxiliares do módulo (`create_tables`, `get_db`, `SessionLocal`) — são infraestrutura, não entidades de domínio.

- **Considerações para evolução do modelo:**
  - Adicionar `risk_assessment` como coluna em `Analysis` para persistir o campo já retornado pela API.
  - Avaliar a extração de `positive_points` e `negative_points` para uma tabela própria (`analysis_points`) caso seja necessário filtrar ou agregar por ponto individualmente.
  - Considerar uma tabela `sector_averages` para cachear médias setoriais calculadas pelo `comparator`, evitando recálculo a cada requisição de análise.
