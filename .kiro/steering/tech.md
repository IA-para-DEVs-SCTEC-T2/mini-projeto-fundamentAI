# Stack Tecnológica

Definição das tecnologias utilizadas no projeto. Onde a tecnologia específica não foi explicitada, a escolha é indicada como inferência.

---

## Backend

| Tecnologia | Papel |
|---|---|
| **Python** | Linguagem principal do backend |
| **yfinance** | Cotações, histórico de preços, DRE histórico e dados de FIIs |
| **fundamentus** | Indicadores fundamentalistas de ações da B3 (fonte principal para ações) |
| **API do Banco Central** | Dados macroeconômicos: SELIC e IPCA |
| **Anthropic API** | Geração das análises via LLM (modelos Claude) |
| **FastAPI** | Framework leve e performático para expor a API REST ao frontend |
| **SQLite / PostgreSQL** | SQLite para desenvolvimento local, PostgreSQL para produção |
| **SQLAlchemy** | ORM para abstração do banco de dados |
| **APScheduler** | Agendamento do ETL diário pós-fechamento do mercado (19h Brasília) |
| **pandas** | Manipulação e processamento de dados tabulares financeiros |

---

## Fontes de Dados por Tipo de Ativo

### Ações (Empresas da B3)

| Fonte | Dados coletados |
|---|---|
| **fundamentus** | P/L, P/VP, ROE, ROIC, Margem Líquida, EV/EBITDA, Dividend Yield, Crescimento Receita 5a, dados do balanço |
| **yfinance** | Cotação atual, histórico de preços, DRE histórico (para CAGR de lucro) |
| **API BCB** | SELIC e IPCA (contexto macroeconômico) |

### FIIs (Fundos de Investimento Imobiliário)

| Fonte | Dados coletados |
|---|---|
| **yfinance** | Cotação, P/VP, P/L, Dividend Yield, histórico de dividendos, crescimento de dividendos |

> **Decisão de design:** fundamentus não suporta FIIs via `get_papel()`. yfinance é a fonte exclusiva para FIIs.

---

## Lógica de Scoring por Tipo de Ativo

O scoring usa indicadores específicos por tipo, mas o **output é idêntico** para ações e FIIs.

### Ações — Indicadores e Pesos

| Indicador | Peso | Threshold máximo |
|---|---|---|
| P/L | 15% | ≤ 10x |
| ROE | 20% | ≥ 20% |
| Dívida Líquida / EBITDA | 15% | ≤ 1x |
| Margem Líquida | 15% | ≥ 20% |
| EV/EBITDA | 10% | ≤ 6x |
| Dividend Yield | 10% | ≥ 8% a.a. |
| Crescimento Lucro YoY | 15% | ≥ 10% a.a. |

### FIIs — Indicadores e Pesos

| Indicador | Peso | Threshold máximo |
|---|---|---|
| P/VP | 30% | ≤ 0.90 (desconto sobre patrimônio) |
| P/L | 15% | ≤ 12x |
| Dividend Yield | 35% | ≥ 10% a.a. |
| Crescimento Dividendos YoY | 20% | ≥ 8% a.a. |

### Output Unificado (igual para ambos)

```python
{
    "score": float,          # 0-100
    "label": str,            # "Excelente" | "Bom" | "Regular" | "Fraco"
    "breakdown": dict,       # pontuação por componente
    "weights": dict,         # pesos utilizados
    "available_indicators": list,
    "asset_type": str        # "stock" | "fii"
}
```

---

## Geração de Análises via LLM (Anthropic)

Os dados coletados e processados são injetados em prompts estruturados e enviados à API da Anthropic.

### Modelos utilizados

| Modelo | Uso indicado |
|---|---|
| `claude-sonnet-4-5` | Análises completas — maior qualidade de raciocínio |
| `claude-haiku-4-5` | Respostas rápidas ou consultas de menor complexidade |

### Fluxo de geração

```
Dados financeiros processados (indicadores por tipo de ativo, macro)
        ↓
backend/prompts/builder.py  → monta o prompt estruturado
        ↓
Anthropic API (Claude)      → gera a análise em formato JSON estruturado
        ↓
backend/api/                → retorna o resultado ao frontend
        ↓
frontend/                   → renderiza veredito, score e explicações
```

### Boas práticas

- Prompts versionados em `backend/prompts/` — nunca hardcoded nas rotas
- Template separado da lógica de injeção de dados
- Tratar erros e timeouts com fallback adequado
- `ANTHROPIC_API_KEY` nunca no código — usar variável de ambiente

---

## Gestão de Tickers Inativos

Tickers sem cotação ou sem dados financeiros são classificados como inativos antes da coleta.

- Tabela `inactive_tickers` no banco armazena os inativos mapeados
- API retorna HTTP 404 com mensagem explicativa para consultas a inativos
- Script `backend/scripts/populate_all_tickers.py` gera `relatorio_inativos.csv`

**Critérios de inatividade:**
1. Preço de mercado zero ou ausente
2. Sem nenhum indicador (ROE, P/L, P/VP nulos) E sem dados financeiros básicos

---

## Fluxo de Dados Completo

```
fundamentus (ações) + yfinance (FIIs + histórico DRE) + BCB (macro)
        ↓
backend/collectors/     → coleta bruta por fonte e tipo de ativo
        ↓
backend/processors/
  asset_classifier.py   → classifica stock/fii, detecta inativos
  indicators.py         → calcula indicadores por tipo
  scoring.py            → score específico por tipo, output unificado
        ↓
Banco de dados          → persistência (tickers, financial_data, indicators)
        ↓
backend/prompts/        → prompt estruturado com dados do tipo correto
        ↓
Anthropic API (Claude)  → análise em JSON estruturado
        ↓
backend/api/            → REST ao frontend (resposta unificada)
        ↓
frontend/               → dashboard, gráficos e veredito
```

### Scripts de Manutenção

| Script | Descrição | Quando executar |
|---|---|---|
| `backend/scripts/populate_all_tickers.py` | Popula banco com todos os ~993 tickers da B3 | Primeira carga ou reprocessamento completo |
| `backend/scripts/update_income_growth.py` | Atualiza CAGR de lucro via yfinance (ações) | Após populate ou mensalmente |
| `backend/scripts/ensure_min_indicators.py` | Verifica e enriquece tickers com < 3 indicadores | Automaticamente após cada ETL |

#### `ensure_min_indicators.py` — Garantia de qualidade de dados

Executado automaticamente ao final de cada rodada do ETL. Garante que todos os tickers ativos tenham pelo menos 3 indicadores disponíveis para o cálculo do score.

**Fluxo por ticker com < 3 indicadores:**
1. **Busca em fonte alternativa (yfinance):** ROE, Margem, P/L, P/VP, DY para ações; P/VP, DY calculado do histórico, crescimento de dividendos para FIIs
2. **Cálculo derivado a partir do banco:** ROE = lucro/patrimônio, Margem = lucro/receita, Dívida/EBITDA, P/VP = preço/VPA, DY = dividendos12m/preço
3. **Se ainda < 3 após todas as tentativas:** move para `inactive_tickers`

```bash
# Verificação completa (padrão — move inativos)
python -m backend.scripts.ensure_min_indicators

# Apenas relatório, sem alterar banco
python -m backend.scripts.ensure_min_indicators --dry-run

# Ticker específico
python -m backend.scripts.ensure_min_indicators --ticker PETR4

# Enriquece sem mover para inativos
python -m backend.scripts.ensure_min_indicators --no-move-inactive
```

---

## Frontend

| Tecnologia | Papel |
|---|---|
| **React** | Framework principal do frontend |
| **Recharts ou Chart.js** | Biblioteca de gráficos para dashboards |
| **Axios** | Cliente HTTP para chamadas à API do backend |
| **React Router** | Navegação entre páginas (Home e Analysis) |

---

## Restrições e Decisões Técnicas

- **Sem dados em tempo real no MVP** — processamento diário pós-fechamento
- **Dados públicos apenas** — nenhuma fonte paga ou proprietária
- **Análise fundamentalista exclusivamente** — sem análise técnica/gráfica
- **Output unificado** — mesmo formato de resposta para ações e FIIs (frontend único)
- **Cobertura de crescimento de lucro:** ~44% das ações têm histórico DRE disponível no yfinance; os demais recebem score neutro nesse componente

---

## IDE e Ambiente de Desenvolvimento

Utilizar o **[Kiro](https://kiro.dev)** como IDE, no modo **Auto**.

- O modo **Auto** permite que o agente execute alterações de forma autônoma
- Os arquivos em `.kiro/steering/` fornecem contexto permanente ao agente
