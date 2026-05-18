# Relatório do Banco de Dados — FundamentAI

> Gerado em: **2026-05-17 18:47**

---

## 1. Visão Geral

| Métrica | Valor |
|---|---|
| Tickers ativos | **1118** |
| — Ações | 938 |
| — FIIs | 180 |
| Tickers inativos | 56 |
| Com score calculado | 1118 / 1118 |
| Análises LLM geradas | 0 |

## 2. Distribuição de Scores


### 2.1 Geral

| Label | Qtd | % | Barra | Média | Mín | Máx |
|---|---:|---:|---|---:|---:|---:|
| **Excelente** | 122 | 10.9% | `██░░░░░░░░░░░░░` | 82.5 | 75.0 | 100.0 |
| **Bom** | 608 | 54.4% | `████████░░░░░░░` | 59.3 | 50.0 | 74.9 |
| **Regular** | 293 | 26.2% | `████░░░░░░░░░░░` | 39.8 | 25.0 | 50.0 |
| **Fraco** | 95 | 8.5% | `█░░░░░░░░░░░░░░` | 21.7 | 18.3 | 24.8 |

### 2.2 Ações vs FIIs


**Ações** (938 tickers)

| Label | Qtd | % | Média | Mín | Máx |
|---|---:|---:|---:|---:|---:|
| Excelente | 26 | 2.8% | 78.9 | 75.0 | 80.0 |
| Bom | 537 | 57.2% | 58.8 | 50.0 | 72.5 |
| Regular | 280 | 29.9% | 39.7 | 25.0 | 50.0 |
| Fraco | 95 | 10.1% | 21.7 | 18.3 | 24.8 |

**FIIs** (180 tickers)

| Label | Qtd | % | Média | Mín | Máx |
|---|---:|---:|---:|---:|---:|
| Excelente | 96 | 53.3% | 83.5 | 75.0 | 100.0 |
| Bom | 71 | 39.4% | 63.2 | 50.0 | 74.9 |
| Regular | 13 | 7.2% | 41.5 | 31.7 | 47.5 |

## 3. Cobertura de Indicadores — Ações

> Base: **938 ações** ativas no banco

> Indicadores ausentes recebem **score neutro (50)** no cálculo.

| Indicador | Preenchidos | Nulos | Cobertura | Barra | Observação |
|---|---:|---:|---:|---|---|
| **ROE** | 777 | 161 | 82.8% | `████████████░░░` ✅ | Peso 20% no score |
| **Margem Líquida** | 511 | 427 | 54.5% | `████████░░░░░░░` ⚠️ | Peso 15% no score |
| **P/L** | 283 | 655 | 30.2% | `█████░░░░░░░░░░` ❌ | Peso 15% no score |
| **P/VP** | 278 | 660 | 29.6% | `████░░░░░░░░░░░` ❌ | Calculado via fundamentus |
| **EV/EBITDA** | 50 | 888 | 5.3% | `█░░░░░░░░░░░░░░` ❌ | Peso 10% no score |
| **Dívida/EBITDA** | 0 | 938 | 0.0% | `░░░░░░░░░░░░░░░` ❌ | Peso 15% no score — derivado de EV/EV_EBITDA |
| **Dividend Yield** | 869 | 69 | 92.6% | `██████████████░` ✅ | Peso 10% no score |
| **CAGR Lucro** | 277 | 661 | 29.5% | `████░░░░░░░░░░░` ❌ | Peso 15% — via yfinance (~44.7% cobertura esperada) |
| **Crescimento Receita 5a** | 793 | 145 | 84.5% | `█████████████░░` ✅ | Via fundamentus |

## 4. Cobertura de Indicadores — FIIs

> Base: **180 FIIs** ativos no banco

> Fonte exclusiva: **yfinance** (fundamentus não suporta FIIs).

| Indicador | Preenchidos | Nulos | Cobertura | Barra | Observação |
|---|---:|---:|---:|---|---|
| **P/VP** | 35 | 145 | 19.4% | `███░░░░░░░░░░░░` ❌ | Peso 30% no score — yfinance retorna `priceToBook` |
| **P/L** | 108 | 72 | 60.0% | `█████████░░░░░░` ⚠️ | Peso 15% no score — via `trailingPE` |
| **Dividend Yield** | 144 | 36 | 80.0% | `████████████░░░` ✅ | Peso 35% no score — normalizado (÷100 se > 1.0) |
| **CAGR Dividendos** | 162 | 18 | 90.0% | `██████████████░` ✅ | Peso 20% no score — calculado do histórico de dividendos |

## 5. Top 20 Ações por Score

| Ticker | Score | Label | ROE | P/L | P/VP | DY | CAGR Lucro | D/EBITDA |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| **BMOB3** | 80.0 | Excelente | 164.0% | — | — | 75.0% | 22.3% | — |
| **CEAB3** | 80.0 | Excelente | 158.0% | — | 91.00 | 47.0% | 790.6% | — |
| **CLSC3** | 80.0 | Excelente | 176.0% | — | — | 67.0% | 10.5% | — |
| **CLSC4** | 80.0 | Excelente | 176.0% | — | — | 65.0% | 10.5% | — |
| **CPLE3** | 80.0 | Excelente | 114.0% | — | — | 72.0% | 31.0% | — |
| **DESK3** | 80.0 | Excelente | 43.0% | — | — | 8.0% | 14.2% | — |
| **ECOR3** | 80.0 | Excelente | 178.0% | — | — | 81.0% | 51.9% | — |
| **FLRY3** | 80.0 | Excelente | 122.0% | — | — | 69.0% | 25.8% | — |
| **FRAS3** | 80.0 | Excelente | 105.0% | — | — | 31.0% | 10.6% | — |
| **GMAT3** | 80.0 | Excelente | 158.0% | — | 91.00 | 43.0% | 20.3% | — |
| **MDIA3** | 80.0 | Excelente | 83.0% | — | 81.00 | 53.0% | 11.0% | — |
| **MLAS3** | 80.0 | Excelente | 58.0% | — | 41.00 | 33.0% | 10.7% | — |
| **PNVL3** | 80.0 | Excelente | 102.0% | — | — | 25.0% | 13.0% | — |
| **RAIL3** | 80.0 | Excelente | 75.0% | — | — | 61.0% | 18.0% | — |
| **SBFG3** | 80.0 | Excelente | 108.0% | — | 79.00 | 51.0% | 17.0% | — |
| **TTEN3** | 80.0 | Excelente | 149.0% | — | — | 11.0% | 12.6% | — |
| **UGPA3** | 80.0 | Excelente | 182.0% | — | — | 45.0% | 21.1% | — |
| **GGPS3** | 79.7 | Excelente | 160.0% | — | — | 22.0% | 9.8% | — |
| **RADL3** | 78.8 | Excelente | 176.0% | — | — | 20.0% | 9.2% | — |
| **BRAV3** | 78.8 | Excelente | 20.0% | — | 76.00 | 7.0% | 111.3% | — |

## 6. Top 20 FIIs por Score

| Ticker | Score | Label | P/VP | DY | CAGR DY | P/L | Preço |
|---|---:|---|---:|---:|---:|---:|---:|
| **BRCR11** | 100.0 | Excelente | 0.52 | 10.8% | 19.6% | 11.3 | R$ 45.48 |
| **PORD11** | 100.0 | Excelente | 0.84 | 14.1% | 23.0% | 1.0 | R$ 8.33 |
| **SPTW11** | 100.0 | Excelente | 0.69 | 13.6% | 10.8% | 6.2 | R$ 39.76 |
| **VRTA11** | 100.0 | Excelente | 0.84 | 13.4% | 19.6% | 11.3 | R$ 76.41 |
| **JSRE11** | 98.2 | Excelente | 0.55 | 9.6% | 16.4% | 9.7 | R$ 60.14 |
| **FPAB11** | 97.1 | Excelente | 0.50 | 10.6% | 5.7% | 3.6 | R$ 204.00 |
| **RNGO11** | 95.3 | Excelente | 0.62 | 11.2% | 13.8% | 13.1 | R$ 51.25 |
| **BMLC11** | 95.1 | Excelente | 0.48 | 8.9% | 17.1% | 6.9 | R$ 99.99 |
| **FIIP11** | 92.5 | Excelente | 0.67 | 12.3% | 14.1% | — | R$ 136.44 |
| **FIGS11** | 92.5 | Excelente | 0.50 | 11.5% | 9.0% | — | R$ 50.07 |
| **RBVA11** | 92.5 | Excelente | 0.88 | 11.2% | 19.2% | — | R$ 9.60 |
| **TRBL11** | 92.5 | Excelente | 0.68 | 15.2% | 18.5% | — | R$ 67.00 |
| **KNCR11** | 88.6 | Excelente | 1.05 | 12.4% | 14.2% | 8.8 | R$ 106.10 |
| **HGBS11** | 88.5 | Excelente | 0.86 | 10.2% | 5.9% | 18.2 | R$ 20.00 |
| **HGLG11** | 87.2 | Excelente | 0.98 | 8.5% | 21.4% | 9.6 | R$ 155.50 |
| **MXRF11** | 86.8 | Excelente | 1.00 | 12.1% | 13.4% | 14.2 | R$ 9.92 |
| **AFHI11** | 85.0 | Excelente | — | 12.1% | 11.9% | 8.9 | R$ 97.11 |
| **ARRI11** | 85.0 | Excelente | — | 16.0% | 25.0% | 5.4 | R$ 5.25 |
| **BRIP11** | 85.0 | Excelente | — | 90.3% | 26.6% | 8.3 | R$ 421.80 |
| **CACR11** | 85.0 | Excelente | — | 37.3% | 73.1% | 4.2 | R$ 38.60 |

## 7. Bottom 10 Ações por Score

| Ticker | Setor | Score | Label | ROE | P/L | DY |
|---|---|---:|---|---:|---:|---:|
| **GAZO3** | — | 18.2 | Fraco | -106.0% | 45.0 | — |
| **AESB3** | Energia Elétrica | 19.0 | Fraco | -87.0% | — | — |
| **ARCZ3** | Madeira e Papel | 19.0 | Fraco | — | -188.0 | — |
| **ARCZ6** | Madeira e Papel | 19.0 | Fraco | — | -186.0 | — |
| **BAHI4** | Diversos | 19.0 | Fraco | — | — | — |
| **BAHI5** | Diversos | 19.0 | Fraco | — | — | — |
| **BRTP3** | — | 19.0 | Fraco | -36.0% | — | — |
| **BRTP4** | — | 19.0 | Fraco | -36.0% | — | — |
| **CCIM3** | Construção Civil | 19.0 | Fraco | -57.0% | — | — |
| **GBIO33** | Medicamentos e Outros Produtos | 19.0 | Fraco | -88.0% | — | — |

## 8. Tickers Inativos

> Total: **56 tickers inativos**

| Motivo | Tipo | Qtd |
|---|---|---:|
| Sem dados financeiros | fii | 24 |
| Sem preço de mercado | stock | 32 |

## 9. Pontos de Atenção

| # | Indicador | Impacto | Causa | Ação sugerida |
|---|---|---|---|---|
| 1 | **Dívida/EBITDA** (938 ações sem dado) | Peso 15% no score — usa neutro (50) | fundamentus não retorna EBITDA diretamente; derivação via EV/EV_EBITDA requer EV_EBITDA > 0 | Rodar `ensure_min_indicators` para tentar via yfinance |
| 2 | **EV/EBITDA** (888 ações sem dado) | Peso 10% no score — usa neutro (50) | fundamentus retorna `000` (ausente) para a maioria | Limitação da fonte — sem alternativa direta |
| 3 | **P/VP FIIs** (145 FIIs sem dado) | Peso 30% no score — usa neutro (50) | yfinance não retorna `priceToBook` para a maioria dos FIIs BR | Calcular via `current_price / book_value_per_share` quando disponível |
| 4 | **DY FIIs** (36 FIIs sem dado) | Peso 35% no score — usa neutro (50) | yfinance não retorna `dividendYield` para alguns FIIs | Calcular via `dividends_12m / current_price` do histórico |
| 5 | **CAGR Lucro ações** (~661 ações sem dado) | Peso 15% no score — usa neutro (50) | Limitação do yfinance: ~44.7% das ações têm DRE histórico | Rodar `update_income_growth` mensalmente |

---

> Relatório gerado automaticamente por `backend/scripts/generate_report.py` em 2026-05-17 18:47.
> Para atualizar: `python -m backend.scripts.generate_report`