# PRD — FundamentAI: Analisador Fundamentalista de Ações e FIIs da B3

**Versão:** 1.0  
**Data:** 2026-05-14  
**Status:** Em desenvolvimento  
**Repositório:** https://github.com/IA-para-DEVs-SCTEC-T2/FundamentAI

---

## 1. Visão Geral e Público-Alvo

### 1.1 O Problema

O mercado de capitais brasileiro conta com mais de 900 ativos ativos listados na B3 (ações e FIIs). Investidores — especialmente os iniciantes — enfrentam uma barreira estrutural para avaliar esses ativos:

- **Dispersão de informações:** dados relevantes estão espalhados em múltiplas plataformas (B3, CVM, corretoras, agregadores pagos).
- **Complexidade interpretativa:** indicadores como EV/EBITDA, ROE e P/VP exigem contexto técnico para serem compreendidos corretamente.
- **Custo de especialistas:** consultorias e plataformas premium estão fora do alcance de pequenos investidores.
- **Falta de padronização:** ações e FIIs têm métricas distintas, dificultando comparações e critérios unificados.
- **Tempo elevado:** uma análise mínima razoável de um único ativo pode levar horas de pesquisa manual.

### 1.2 A Solução

O **FundamentAI** é uma plataforma web que consolida dados financeiros públicos de ações e FIIs da B3, aplica critérios objetivos de análise fundamentalista e entrega análises estruturadas geradas por IA — com viés educativo e linguagem acessível.

> **Disclaimer obrigatório:** O FundamentAI não fornece recomendações de investimento. As análises são informativas e baseadas em dados históricos. A decisão final é sempre do usuário.

### 1.3 Perfis de Usuário

| Persona | Descrição | Necessidade Principal |
|---|---|---|
| **Investidor Iniciante** | Pessoa física começando na B3, sem formação financeira formal | Entender indicadores básicos com linguagem acessível e obter uma avaliação rápida do ativo |
| **Investidor Intermediário** | Já opera há algum tempo, busca sistematizar sua análise | Score unificado, comparação setorial e histórico de indicadores |
| **Estudante de Finanças** | Cursa graduação/MBA em finanças ou economia | Ferramenta educativa para entender a aplicação prática de indicadores |

---

## 2. Requisitos

### 2.1 Requisitos Funcionais

| ID | Requisito | Prioridade |
|---|---|---|
| RF-01 | Consulta de ativo por ticker (ex: PETR4, HGLG11) — ações e FIIs da B3 | Alta |
| RF-02 | Classificação automática do tipo de ativo: `stock` ou `fii` | Alta |
| RF-03 | Cálculo de score fundamentalista unificado (0–100) com indicadores específicos por tipo de ativo | Alta |
| RF-04 | Exibição de classificação qualitativa do score: Excelente / Bom / Regular / Fraco | Alta |
| RF-05 | Geração de análise estruturada via LLM (Claude) com veredito, pontos positivos/negativos, risco e conclusão | Alta |
| RF-06 | Injeção de contexto macroeconômico (SELIC e IPCA) nos prompts de análise | Alta |
| RF-07 | Dashboard visual com gráficos de indicadores e histórico de preços | Média |
| RF-08 | Comparação setorial dos indicadores do ativo analisado | Média |
| RF-09 | Identificação e bloqueio de tickers inativos com retorno HTTP 404 e mensagem explicativa | Alta |
| RF-10 | ETL diário automatizado pós-fechamento do mercado (19h, fuso de Brasília) | Alta |
| RF-11 | Geração de relatórios operacionais: tickers inativos, nulos e anomalias de indicadores | Média |
| RF-12 | Script de população inicial do banco com todos os tickers da B3 (~993 ativos) | Alta |
| RF-13 | Garantia de qualidade de dados: tickers com menos de 3 indicadores são enriquecidos ou movidos para inativos | Alta |

### 2.2 Requisitos Não Funcionais

| ID | Requisito | Critério de Aceitação |
|---|---|---|
| RNF-01 | **Performance** — Resposta da API para consulta de ticker já processado | ≤ 2 segundos (P95) |
| RNF-02 | **Performance** — Geração de análise via LLM | ≤ 15 segundos (P95) |
| RNF-03 | **Disponibilidade** — Dados atualizados diariamente após o fechamento do pregão | Atualização concluída até às 21h (horário de Brasília) |
| RNF-04 | **Segurança** — Nenhuma chave de API exposta no código | `ANTHROPIC_API_KEY` exclusivamente via variável de ambiente (`.env`) |
| RNF-05 | **Segurança** — Dados utilizados são públicos; nenhum dado pessoal armazenado no MVP | Zero PII no banco de dados do MVP |
| RNF-06 | **Escalabilidade** — Backend stateless com suporte a escalabilidade horizontal | Compatível com deploy em containers (Docker) |
| RNF-07 | **Usabilidade** — Interface navegável sem treinamento prévio por investidor iniciante | Tarefa principal (consultar ativo) concluída em ≤ 3 cliques |
| RNF-08 | **Manutenibilidade** — Lógica de negócio isolada em `processors/`, sem dependência de banco ou API | Cobertura de testes unitários ≥ 80% nos processadores |
| RNF-09 | **Portabilidade** — Suporte a SQLite (dev) e PostgreSQL (prod) via abstração SQLAlchemy | Sem SQL vendor-specific no código da aplicação |
| RNF-10 | **Rastreabilidade** — Prompts enviados à LLM versionados, nunca hardcoded nas rotas | Templates em `backend/prompts/` |

---

## 3. Regras de Negócio

### 3.1 Classificação de Ativos

A classificação de um ativo como **FII** ou **ação** é determinada pelo campo `b3_type` proveniente da B3.

**Regra de negócio:**

- Ativos com `b3_type` indicando fundo imobiliário são classificados como **FII** (ex: `HGLG11`, `XPML11`, `MXRF11`).
- Ativos com `b3_type` de ação — incluindo `ON`, `PN`, `UNT` e variantes (`ON NM`, `PN N2`, `UNT N2`, etc.) — são classificados como **ação**, independentemente do sufixo numérico.

**Por que o sufixo `11` não é definitivo:**

UNITs (certificados que representam conjuntos de ações ON + PN) também terminam em `11` mas são ações, não FIIs. Exemplos:

| Ticker | `b3_type` | Classificação Correta |
|---|---|---|
| `HGLG11` | FII | `fii` |
| `XPML11` | FII | `fii` |
| `SAPR11` | UNT | `stock` |
| `TAEE11` | UNT N2 | `stock` |
| `SANB11` | UNT | `stock` |
| `VALE3` | ON NM | `stock` |
| `MGLU3` | ON NM | `stock` |
| `BBAS3` | ON NM | `stock` |
| `PETR4` | PN N2 | `stock` |
| `ITUB4` | PN N1 | `stock` |
| `BBDC4` | PN N1 | `stock` |

A classificação é realizada pelo módulo `backend/processors/asset_classifier.py`, alimentado pelos dados de `b3_type` coletados da B3 durante o script `populate_all_tickers.py`.

### 3.2 Cálculo do Score — Ações

O score é ponderado com base em 7 indicadores. Cada indicador recebe pontuação proporcional ao seu threshold máximo de referência:

| Indicador | Peso | Threshold de Referência (100%) |
|---|---|---|
| P/L | 15% | ≤ 10x |
| ROE | 20% | ≥ 20% |
| Dívida Líquida / EBITDA | 15% | ≤ 1x |
| Margem Líquida | 15% | ≥ 20% |
| EV/EBITDA | 10% | ≤ 6x |
| Dividend Yield | 10% | ≥ 8% a.a. |
| Crescimento Lucro YoY (CAGR) | 15% | ≥ 10% a.a. |

- **Fonte principal:** `fundamentus` (P/L, ROE, Margem, EV/EBITDA, DY).
- **Fonte complementar:** `yfinance` (histórico DRE para CAGR de lucro).
- **Cobertura do CAGR:** ~44% das ações têm histórico DRE disponível no yfinance; os demais recebem pontuação neutra neste componente.

### 3.3 Cálculo do Score — FIIs

| Indicador | Peso | Threshold de Referência (100%) |
|---|---|---|
| P/VP | 30% | ≤ 0,90 (desconto sobre patrimônio) |
| P/L | 15% | ≤ 12x |
| Dividend Yield | 35% | ≥ 10% a.a. |
| Crescimento Dividendos YoY (CAGR) | 20% | ≥ 8% a.a. |

- **Fonte exclusiva:** `yfinance` (fundamentus não suporta FIIs via `get_papel()`).

### 3.4 Classificação Qualitativa do Score

| Faixa | Classificação |
|---|---|
| 75 – 100 | Excelente |
| 50 – 74 | Bom |
| 25 – 49 | Regular |
| 0 – 24 | Fraco |

### 3.5 Contexto Macroeconômico

Injetado em todos os prompts de análise da LLM:

| Dado | API | Série |
|---|---|---|
| SELIC | Banco Central do Brasil (SGS) | Série 11 |
| IPCA | Banco Central do Brasil (SGS) | Série 433 |

### 3.6 Critérios de Inatividade de Tickers

Um ticker é classificado como **inativo** quando atende a **pelo menos um** dos critérios abaixo:

1. Preço de mercado zero ou ausente.
2. Nenhum indicador disponível (ROE, P/L e P/VP todos nulos) **e** sem dados financeiros básicos.
3. Menos de 3 indicadores disponíveis após tentativas de enriquecimento em fontes alternativas.

Tickers inativos são movidos para a tabela `inactive_tickers` e excluídos do pipeline de análise. Consultas a esses tickers retornam HTTP 404 com mensagem explicativa.

### 3.7 Garantia Mínima de Qualidade de Dados

Ao final de cada rodada do ETL, o script `ensure_min_indicators.py` é executado automaticamente:

1. Identifica tickers com menos de 3 indicadores disponíveis.
2. Busca indicadores faltantes em fonte alternativa (yfinance).
3. Calcula indicadores derivados a partir dos dados já no banco (ex: `ROE = lucro / patrimônio`).
4. Se ainda < 3 após todas as tentativas → move para `inactive_tickers`.

### 3.8 Output Unificado da API

O formato de resposta é **idêntico** para ações e FIIs, garantindo que o frontend não precise diferenciar o tipo de ativo na camada de renderização:

```json
{
  "score": 72.5,
  "label": "Bom",
  "breakdown": { "roe": 18.0, "pl": 10.5, "..." : "..." },
  "weights": { "roe": 0.20, "pl": 0.15, "..." : "..." },
  "available_indicators": ["roe", "pl", "margem_liquida"],
  "asset_type": "stock"
}
```

---

## 4. Arquitetura

### 4.1 Visão Geral

A arquitetura segue um modelo de **camadas desacopladas** com separação clara entre coleta, processamento, persistência, geração de análise e apresentação.

```
┌─────────────────────────────────────────────────────────────────┐
│                        FONTES DE DADOS                          │
│  fundamentus (ações)  │  yfinance (ações + FIIs)  │  BCB (macro)│
└───────────┬───────────┴──────────────┬────────────┴──────┬──────┘
            │                          │                    │
            ▼                          ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    backend/collectors/                           │
│  fundamentus.py  │  yfinance.py  │  fii.py  │  bacen.py         │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    backend/processors/                           │
│  asset_classifier.py  │  indicators.py  │  scoring.py           │
│                        comparator.py                            │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│              Banco de Dados (SQLite / PostgreSQL)                │
│  tickers │ inactive_tickers │ financial_data │ indicators        │
│                           analyses                               │
└──────────────────────────────┬──────────────────────────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
┌─────────────────────┐              ┌─────────────────────────┐
│  backend/prompts/   │              │      Anthropic API       │
│  builder.py         │ ──────────▶  │  claude-sonnet-4-5       │
└─────────────────────┘              │  claude-haiku-4-5        │
                                     └────────────┬────────────┘
                                                  │
                                                  ▼
                                     ┌─────────────────────────┐
                                     │      backend/api/        │
                                     │  GET /api/ticker/{t}     │
                                     │  POST /api/analysis/{t}  │
                                     └────────────┬────────────┘
                                                  │
                                                  ▼
                                     ┌─────────────────────────┐
                                     │        frontend/         │
                                     │  React + Recharts/Chart  │
                                     └─────────────────────────┘
```

### 4.2 Responsabilidades por Camada

| Camada | Módulo | Responsabilidade |
|---|---|---|
| Coleta | `backend/collectors/` | Acesso às fontes externas; sem lógica de negócio |
| Processamento | `backend/processors/` | Cálculo puro de indicadores e scoring; sem acesso a banco ou API |
| Persistência | `backend/db/` | Models SQLAlchemy + Repository pattern (CRUD e upsert) |
| Análise IA | `backend/prompts/` | Construção de prompts estruturados; Anthropic API |
| API REST | `backend/api/` | Roteamento HTTP; delegação para processors e db |
| Orquestração | `backend/etl/pipeline.py` | ETL diário; agendado via APScheduler às 19h |
| Apresentação | `frontend/` | Dashboard React; consumo da API via Axios |

### 4.3 Modelo de Dados

| Tabela | Conteúdo |
|---|---|
| `tickers` | Ativos ativos: ticker, `asset_type` (`stock`/`fii`), `b3_type` (ON, PN, UNT...) |
| `inactive_tickers` | Tickers inativos: ticker, `asset_type`, motivo, último preço |
| `financial_data` | Dados financeiros brutos por data de referência |
| `indicators` | Indicadores calculados por tipo de ativo e data |
| `analyses` | Análises geradas pela LLM: JSON estruturado + metadados |

---

## 5. User Stories

### US-01 — Consultar análise de uma ação

> **Como** investidor iniciante,  
> **Quero** digitar um ticker (ex: `PETR4`) e receber uma análise fundamentalista completa,  
> **Para que** eu entenda rapidamente se o ativo é atrativo sem precisar pesquisar em múltiplas fontes.

**Critérios de aceite:**

- [ ] O campo de busca aceita tickers em maiúsculas e minúsculas.
- [ ] O sistema identifica automaticamente se o ticker é ação ou FII.
- [ ] O score (0–100) e a classificação qualitativa são exibidos em destaque.
- [ ] A análise textual gerada pela IA apresenta: veredito, pontos positivos, pontos negativos, avaliação de risco e conclusão.
- [ ] A resposta é entregue em até 15 segundos (P95).
- [ ] O disclaimer de não-recomendação é exibido de forma visível na página.

---

### US-02 — Consultar análise de um FII

> **Como** investidor intermediário,  
> **Quero** analisar um FII (ex: `HGLG11`) com indicadores específicos de fundos imobiliários,  
> **Para que** eu avalie a atratividade do fundo com base em métricas relevantes para esse tipo de ativo.

**Critérios de aceite:**

- [ ] O sistema identifica o ticker como FII pelo `b3_type` e aplica os indicadores corretos (P/VP, DY, Crescimento DY, P/L).
- [ ] O score apresenta breakdown dos 4 componentes com seus respectivos pesos.
- [ ] A análise da IA contextualiza os dados com SELIC e IPCA atuais.
- [ ] O formato de resposta é idêntico ao de ações (score, label, breakdown, asset_type).

---

### US-03 — Verificar ticker inativo

> **Como** usuário,  
> **Quero** ser informado claramente quando consultar um ticker inativo ou inexistente,  
> **Para que** eu entenda por que a análise não está disponível e não fique confuso com uma tela de erro genérica.

**Critérios de aceite:**

- [ ] Consultas a tickers inativos retornam HTTP 404.
- [ ] A mensagem exibida no frontend é explicativa: informa que o ticker não possui dados suficientes para análise.
- [ ] O sistema não tenta processar ou exibir dados parciais de tickers inativos.

---

### US-04 — Comparar indicadores com o setor

> **Como** investidor intermediário,  
> **Quero** ver os indicadores do ativo comparados com a média do setor,  
> **Para que** eu contextualize se o ativo está acima ou abaixo dos seus pares.

**Critérios de aceite:**

- [ ] A página de análise exibe um componente de comparação setorial.
- [ ] Os indicadores do ativo são apresentados lado a lado com a média do setor (quando disponível).
- [ ] A ausência de dado setorial não quebra a experiência; o componente é ocultado ou exibe mensagem amigável.
- [ ] A comparação usa os mesmos indicadores do scoring do tipo de ativo.

---

### US-05 — Entender o que significa cada indicador

> **Como** estudante de finanças,  
> **Quero** ler explicações didáticas sobre cada indicador exibido na análise,  
> **Para que** eu aprenda o significado prático de P/L, ROE, DY e outros enquanto uso a plataforma.

**Critérios de aceite:**

- [ ] Cada indicador exibido no dashboard possui um tooltip ou seção de explicação em linguagem acessível.
- [ ] A explicação contextualiza o indicador para o tipo de ativo (ação ou FII).
- [ ] As explicações são geradas ou curadas com precisão técnica — sem simplificações que induzam erros de interpretação.

---

### US-06 — Dados sempre atualizados

> **Como** usuário recorrente,  
> **Quero** que os dados dos ativos sejam atualizados automaticamente após o fechamento do pregão,  
> **Para que** minhas análises reflitam as informações mais recentes disponíveis.

**Critérios de aceite:**

- [ ] O ETL é executado automaticamente às 19h (fuso de Brasília) em dias úteis.
- [ ] A data da última atualização é exibida na interface.
- [ ] Falhas no ETL são registradas em log sem interromper a disponibilidade da API para dados já processados.

---

## 6. Fluxo de Funcionamento

```
Usuário digita ticker (ex: PETR4 ou HGLG11)
        │
        ▼
GET /api/ticker/{ticker}
        │
        ├── Ticker inativo? ──► HTTP 404 + mensagem explicativa
        │
        ├── Ticker não encontrado? ──► HTTP 404
        │
        ▼
backend/processors/asset_classifier.py
  └── Classifica: stock | fii
        │
        ▼
Indicadores já no banco? (atualização de hoje)
  ├── Sim ──► Retorna dados em cache
  └── Não ──► Coleta sob demanda (fallback)
        │
        ▼
POST /api/analysis/{ticker}
        │
        ▼
backend/processors/scoring.py
  └── Calcula score 0-100 (lógica específica por tipo)
        │
        ▼
backend/processors/comparator.py
  └── Comparação setorial
        │
        ▼
backend/prompts/builder.py
  └── Monta prompt estruturado:
      • Indicadores calculados (por tipo de ativo)
      • Contexto macro (SELIC + IPCA do BCB)
      • Score e breakdown
        │
        ▼
Anthropic API (Claude)
  ├── claude-sonnet-4-5 (análise completa)
  └── claude-haiku-4-5 (consultas rápidas)
        │
        ▼
Resposta JSON estruturada:
  • veredito (Positivo / Neutro / Negativo)
  • score + label
  • pontos_positivos / pontos_negativos
  • avaliacao_risco
  • sugestao_de_momento (≠ recomendação)
  • conclusao + nivel_de_confianca
        │
        ▼
frontend/ renderiza:
  • ScoreCard — score e classificação
  • IndicatorTable — indicadores com explicações
  • Chart — histórico de preços / gráficos
  • Verdict — análise da IA com veredito
```

### 6.1 ETL Diário (Pipeline Autônomo)

```
19h Brasília (APScheduler)
        │
        ▼
backend/etl/pipeline.py  →  run_full_pipeline()
        │
        ├── collectors/fundamentus.py    (ações — P/L, ROE, Margem, EV/EBITDA, DY)
        ├── collectors/yfinance.py       (ações — cotação + histórico DRE)
        ├── collectors/fii.py            (FIIs — todos os indicadores)
        └── collectors/bacen.py          (SELIC + IPCA)
        │
        ▼
processors/asset_classifier.py  →  classifica + detecta inativos
        │
        ▼
processors/indicators.py   →  calcula indicadores por tipo
        │
        ▼
db/repository.py           →  upsert em financial_data + indicators
        │
        ▼
scripts/ensure_min_indicators.py  →  enriquece ou move para inactive_tickers
        │
        ▼
reports/ (CSV)  →  banco_analise_nulos.csv | relatorio_inativos.csv | relatorio_anomalias.csv
```

---

## 7. Stack Tecnológica

### 7.1 Backend

| Tecnologia | Versão | Papel | Justificativa |
|---|---|---|---|
| **Python** | ≥ 3.8 | Linguagem principal | Ecossistema maduro para dados financeiros e integração com yfinance/fundamentus |
| **FastAPI** | 0.115.x | API REST | Framework assíncrono, documentação automática (OpenAPI), alta performance |
| **Uvicorn** | 0.34.x | Servidor ASGI | Compatível com FastAPI; suporte a async I/O |
| **SQLAlchemy** | 2.0.x | ORM | Abstração de banco permite trocar SQLite por PostgreSQL sem alterar o código |
| **pandas** | ≥ 2.3.0 | Processamento de dados | Padrão de fato para manipulação de dados tabulares financeiros |
| **yfinance** | 0.2.x | Coleta de dados | Acesso gratuito a cotações, histórico DRE e dados de FIIs |
| **fundamentus** | 0.3.x | Coleta de dados (ações) | Fonte principal de indicadores fundamentalistas de ações da B3 |
| **anthropic** | 0.52.x | Geração de análises | Acesso a Claude (Sonnet e Haiku) via Anthropic API |
| **APScheduler** | 3.10.x | Agendamento do ETL | ETL diário às 19h sem dependência de cron externo |
| **python-dotenv** | 1.0.x | Variáveis de ambiente | Gerenciamento seguro de `ANTHROPIC_API_KEY` e `DATABASE_URL` |
| **requests** | ≥ 2.28.0 | HTTP client | Chamadas à API pública do Banco Central (BCB/SGS) |

### 7.2 Inteligência Artificial

| Modelo | Uso | Justificativa |
|---|---|---|
| `claude-sonnet-4-5` | Análises completas de ativos | Maior qualidade de raciocínio e capacidade de síntese de dados financeiros |
| `claude-haiku-4-5` | Consultas rápidas ou de menor complexidade | Menor latência e custo; adequado para respostas diretas |

**Boas práticas de integração com a Anthropic API:**
- Prompts versionados em `backend/prompts/` — nunca hardcoded nas rotas.
- Template separado da lógica de injeção de dados.
- Tratamento de erros e timeouts com fallback adequado.
- `ANTHROPIC_API_KEY` exclusivamente via variável de ambiente.

### 7.3 Frontend

| Tecnologia | Papel | Justificativa |
|---|---|---|
| **React** | Framework principal | Componentes reutilizáveis (ScoreCard, IndicatorTable, Chart, Verdict); ecossistema amplo |
| **Recharts / Chart.js** | Gráficos e visualizações | Bibliotecas maduras para dashboards financeiros com suporte a gráficos de linha e barra |
| **Axios** | Cliente HTTP | Chamadas à API do backend com interceptors e tratamento de erros centralizado |
| **React Router** | Navegação | SPA com 2 rotas principais: Home (busca) e Analysis (dashboard do ativo) |

### 7.4 Banco de Dados

| Ambiente | Banco | Justificativa |
|---|---|---|
| Desenvolvimento | SQLite | Zero configuração, arquivo local, ideal para desenvolvimento e testes |
| Produção | PostgreSQL | Robustez, concorrência e suporte a queries analíticas |

A abstração via SQLAlchemy garante portabilidade total entre os dois motores sem alteração de código.

### 7.5 Fontes de Dados por Tipo de Ativo

| Fonte | Tipo de Ativo | Dados Fornecidos |
|---|---|---|
| **fundamentus** | Ações | P/L, P/VP, ROE, ROIC, Margem Líquida, EV/EBITDA, Dividend Yield, Crescimento Receita 5a |
| **yfinance** | Ações + FIIs | Cotação atual, histórico de preços, DRE histórico (CAGR de lucro), dados completos de FIIs |
| **API BCB (SGS)** | Ambos | SELIC (série 11) e IPCA (série 433) |

> **Decisão de design:** `fundamentus` não suporta FIIs via `get_papel()`. `yfinance` é a fonte exclusiva para fundos imobiliários.

---

## 8. Próximos Passos (Roadmap)

### 8.1 MVP (v1.0) — Escopo Atual

- [x] Consulta por ticker — ações e FIIs ativos da B3
- [x] Score fundamentalista unificado (0–100) com indicadores específicos por tipo
- [x] Análise estruturada gerada por LLM (Claude) com veredito e explicações
- [x] Contexto macroeconômico (SELIC e IPCA) nos prompts
- [x] ETL diário automatizado (APScheduler, 19h Brasília)
- [x] Identificação e bloqueio de tickers inativos
- [x] Dashboard React com gráficos (ScoreCard, IndicatorTable, Chart, Verdict)
- [x] Comparação setorial de indicadores
- [x] Garantia de qualidade de dados (ensure_min_indicators)
- [x] Relatórios operacionais (inativos, nulos, anomalias)

### 8.2 v1.1 — Qualidade e Cobertura

| Funcionalidade | Motivação |
|---|---|
| Vacância física e financeira de FIIs de tijolo | Indicador relevante para avaliação de risco de FIIs |
| Cap Rate de FIIs | Métrica padrão do mercado imobiliário |
| Histórico de análises por ticker | Permite ao usuário acompanhar a evolução do ativo ao longo do tempo |
| Modo escuro no frontend | Preferência comum de usuários de plataformas financeiras |

### 8.3 v2.0 — Expansão e Personalização

| Funcionalidade | Motivação |
|---|---|
| Carteiras personalizadas | Usuário monta e acompanha uma seleção de ativos |
| Alertas inteligentes (e-mail / push) | Notificação quando score de um ativo supera ou cai abaixo de threshold |
| Dados em tempo real (nível premium) | Diferencial competitivo para usuários avançados |
| Análise de ativos do mercado americano (NYSE, NASDAQ) | Expansão do público-alvo e ticket médio |
| Machine Learning para scoring avançado | Modelo preditivo treinado em dados históricos de desempenho dos ativos |
| Autenticação de usuário | Pré-requisito para carteiras, alertas e preferências pessoais |

### 8.4 Fora do Escopo (Decisão Permanente do MVP)

- Recomendação direta de compra/venda.
- Análise técnica/gráfica (candles, médias móveis, RSI).
- Análise de criptoativos.
- Integração com corretoras (execução de ordens).

---

*Este documento é vivo e deve ser atualizado a cada ciclo de planejamento.*
