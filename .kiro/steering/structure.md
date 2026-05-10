# Estrutura do Projeto

Organização de diretórios: backend Python (coleta, processamento, ETL e API) e frontend React (dashboard e visualizações).

---

## Estrutura de Diretórios

```
/
├── backend/
│   ├── collectors/              # Coleta de dados por fonte e tipo de ativo
│   │   ├── yfinance.py          # Cotações, histórico de preços, DRE (ações)
│   │   ├── fundamentus.py       # Indicadores fundamentalistas (ações da B3)
│   │   ├── fii.py               # Dados de FIIs exclusivamente via yfinance
│   │   ├── income_history.py    # Histórico DRE via yfinance (CAGR de lucro)
│   │   └── bacen.py             # SELIC e IPCA via API do Banco Central
│   │
│   ├── processors/              # Processamento, classificação e scoring
│   │   ├── asset_classifier.py  # Classifica stock/fii, detecta inativos
│   │   ├── indicators.py        # Cálculo de indicadores por tipo de ativo
│   │   ├── scoring.py           # Score específico por tipo, output unificado
│   │   └── comparator.py        # Comparação setorial
│   │
│   ├── etl/                     # Orquestração do pipeline diário
│   │   └── pipeline.py          # ETL pós-fechamento do mercado (19h Brasília)
│   │
│   ├── prompts/                 # Geração de prompts estruturados para LLM
│   │   └── builder.py           # Monta prompt com dados + indicadores + macro
│   │
│   ├── api/                     # API REST que serve os dados ao frontend
│   │   ├── routes/
│   │   │   ├── ticker.py        # GET /api/ticker/{ticker} (ações e FIIs)
│   │   │   └── analysis.py      # POST /api/analysis/{ticker}
│   │   └── main.py              # Entry point da API
│   │
│   ├── db/                      # Modelos e acesso ao banco de dados
│   │   ├── models.py            # Ticker, FinancialData, Indicators, Analysis,
│   │   │                        # InactiveTicker
│   │   └── repository.py        # Repository pattern com CRUD e upsert
│   │
│   ├── scripts/                 # Scripts de manutenção e população do banco
│   │   ├── populate_all_tickers.py   # Popula banco com todos os tickers da B3
│   │   ├── update_income_growth.py   # Atualiza CAGR de lucro via yfinance
│   │   ├── ensure_min_indicators.py  # Verifica e enriquece indicadores (≥3 por ticker)
│   │   ├── data_retention_cleanup.py # Limpeza trimestral conforme política de retenção
│   │   └── fix_zero_indicators.py    # Corrige zeros inválidos do fundamentus
│   │
│   ├── reports/                 # Relatórios gerados automaticamente (não versionados)
│   │   ├── banco_analise_nulos.csv   # Campos nulos por ticker (após populate)
│   │   ├── relatorio_inativos.csv    # Tickers inativos com motivo e tipo
│   │   └── relatorio_anomalias.csv   # Indicadores fora do range (compliance)
│   │
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/          # Componentes reutilizáveis
│   │   │   ├── ScoreCard/
│   │   │   ├── IndicatorTable/
│   │   │   ├── Chart/
│   │   │   └── Verdict/
│   │   │
│   │   ├── pages/               # Páginas da aplicação
│   │   │   ├── Home/            # Busca por ticker
│   │   │   └── Analysis/        # Dashboard de análise do ativo
│   │   │
│   │   ├── services/            # Chamadas à API do backend
│   │   ├── hooks/               # Custom hooks React
│   │   ├── utils/               # Funções auxiliares
│   │   └── App.jsx
│   │
│   ├── public/
│   └── package.json
│
├── docs/                        # Documentação do projeto
├── .kiro/                       # Configurações e steering do Kiro
│   ├── hooks/                   # Hooks do Kiro (ex: prompt-logger)
│   ├── scripts/                 # Scripts auxiliares do Kiro
│   ├── prompt-logs/             # Logs de prompts por branch
│   ├── specs/                   # Specs de funcionalidades
│   └── steering/                # Contexto permanente do projeto
├── .env.example                 # Template de variáveis de ambiente
└── README.md
```

---

## Responsabilidades por Camada

### `backend/collectors/`

Cada arquivo é responsável por uma fonte de dados específica ou tipo de ativo.

| Arquivo | Responsabilidade |
|---|---|
| `yfinance.py` | Cotações, histórico de preços e DRE de ações |
| `fundamentus.py` | Indicadores fundamentalistas de ações (fonte principal) |
| `fii.py` | Todos os dados de FIIs via yfinance |
| `income_history.py` | Histórico de DRE para cálculo de CAGR de lucro |
| `bacen.py` | SELIC e IPCA via API pública do BCB |

### `backend/processors/`

Lógica pura de cálculo e scoring. Sem dependência de banco ou API — facilita testes unitários.

| Arquivo | Responsabilidade |
|---|---|
| `asset_classifier.py` | Classifica ticker como `stock` ou `fii`; detecta inativos |
| `indicators.py` | Calcula indicadores por tipo de ativo |
| `scoring.py` | Score 0-100 com lógica específica por tipo, output unificado |
| `comparator.py` | Comparação setorial de indicadores |

### `backend/db/models.py`

Tabelas do banco de dados:

| Tabela | Conteúdo |
|---|---|
| `tickers` | Ativos ativos (ações e FIIs) com tipo normalizado (`asset_type`) e tipo B3 (`b3_type`) |
| `inactive_tickers` | Tickers inativos com tipo (`asset_type`), motivo e último preço conhecido |
| `financial_data` | Dados financeiros brutos — campos distintos para ações e FIIs |
| `indicators` | Indicadores calculados — campos distintos por tipo de ativo |
| `analyses` | Análises geradas pela LLM |

#### Coluna `asset_type`

Presente em **todas as tabelas de tickers** (`tickers` e `inactive_tickers`):

| Valor | Significado |
|---|---|
| `"stock"` | Ação (empresa da B3) |
| `"fii"` | Fundo de Investimento Imobiliário |

A classificação é feita automaticamente pelo módulo `processors/asset_classifier.py` com base no símbolo:
- Tickers terminados em `11` → `"fii"` (ex: HGLG11, XPML11)
- Demais → `"stock"` (ex: PETR4, VALE3)

#### Coluna `b3_type`

Tipo original da B3, presente em `tickers` e `inactive_tickers`:

| Exemplos | Descrição |
|---|---|
| `ON`, `ON NM`, `ON N1`, `ON N2` | Ação Ordinária (diferentes segmentos) |
| `PN`, `PN N1`, `PN N2`, `PNA`, `PNB` | Ação Preferencial |
| `UNT`, `UNT N2` | Units |
| `DR3` | Brazilian Depositary Receipt |

### `backend/scripts/`

Scripts de manutenção executados manualmente ou via ETL:

| Script | Descrição | Quando executar |
|---|---|---|
| `populate_all_tickers.py` | Popula banco com todos os tickers da B3 | Primeira carga ou reprocessamento |
| `update_income_growth.py` | Atualiza CAGR de lucro via yfinance | Após populate ou mensalmente |
| `ensure_min_indicators.py` | Verifica e enriquece tickers com < 3 indicadores | **Automático após cada ETL** |
| `fix_zero_indicators.py` | Corrige zeros inválidos do fundamentus | Manutenção pontual |

```bash
# Popula banco com todos os tickers da B3 (retoma de onde parou)
python -m backend.scripts.populate_all_tickers

# Atualiza CAGR de lucro via yfinance para todas as ações
python -m backend.scripts.update_income_growth

# Verifica e enriquece indicadores (mínimo 3 por ticker)
python -m backend.scripts.ensure_min_indicators

# Apenas relatório sem alterar banco
python -m backend.scripts.ensure_min_indicators --dry-run
```

#### Garantia de qualidade — `ensure_min_indicators.py`

Executado automaticamente ao final de cada rodada do ETL (`run_full_pipeline`).
Garante que todos os tickers ativos tenham pelo menos **3 indicadores disponíveis** para o cálculo do score.

Fluxo por ticker com < 3 indicadores:
1. Busca em fonte alternativa (yfinance)
2. Calcula indicadores derivados a partir dos dados já no banco
3. Se ainda < 3 → move para `inactive_tickers`

### `backend/api/routes/ticker.py`

- Detecta tipo do ativo (ação ou FII) automaticamente pelo símbolo
- Retorna HTTP 404 com mensagem explicativa para tickers inativos
- Resposta unificada (`TickerResponse`) para ações e FIIs

---

## Convenções

- Nomes de arquivos e pastas em `snake_case` no backend (Python)
- Nomes de componentes e pastas em `PascalCase` no frontend (React)
- Nomes de arquivos de serviço e utilitários em `camelCase` no frontend
- Cada módulo do backend tem responsabilidade única e bem definida
- Lógica de negócio fica em `processors/`, nunca em `api/` ou `etl/`
- Constantes de tipo de ativo: `ASSET_TYPE_STOCK = "stock"`, `ASSET_TYPE_FII = "fii"`
