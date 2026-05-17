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

---

## 10. Análise Crítica — Viabilidade do Projeto como Fonte de Análise

> ⚠️ **Esta seção requer decisão do time.** Os dados abaixo evidenciam limitações estruturais que impactam diretamente a confiabilidade dos scores gerados.

### 10.1 O Problema Central: Scores Construídos sobre Estimativas

O score fundamentalista é calculado com **7 indicadores para ações** e **4 para FIIs**. Quando um indicador está ausente, o sistema atribui **50 pontos (neutro)** — um valor estimado, não real.

O resultado prático é que **a maioria dos scores não reflete a realidade financeira da empresa**, mas sim uma média entre os poucos indicadores disponíveis e estimativas neutras para os ausentes.

#### Quanto do score de uma ação típica é real vs estimado?

| Indicador | Peso | Cobertura real | Tickers com valor estimado |
|---|---|---|---|
| ROE | 20% | 82.8% | ~161 ações |
| Margem Líquida | 15% | 54.5% | ~427 ações |
| **Dívida/EBITDA** | **15%** | **0.0%** | **938 ações (100%)** |
| P/L | 15% | 30.2% | ~655 ações |
| **CAGR Lucro** | **15%** | **29.5%** | **~661 ações** |
| EV/EBITDA | 10% | 5.3% | ~888 ações |
| Dividend Yield | 10% | 92.6% | ~69 ações |

> **Para uma ação mediana da B3:** ROE ✅ + DY ✅ + Margem ⚠️ + os outros 4 estimados = **score com 55% do peso baseado em estimativas neutras.**

> **Para uma ação sem P/L, P/VP, EV/EBITDA, Dívida/EBITDA e CAGR** (cenário comum): score calculado com apenas ROE + DY = **apenas 30% do peso com dados reais.**

---

### 10.2 Indicadores Críticos Ausentes e Suas Implicações

#### Dívida/EBITDA — 0% de cobertura (938 ações)

Este é o indicador de **risco financeiro** mais importante da análise. Sem ele, o sistema não consegue distinguir:
- Uma empresa saudável com caixa líquido positivo
- Uma empresa altamente alavancada à beira da insolvência

**Impacto:** empresas com dívida crítica recebem o mesmo score neutro (50) que empresas sem dívida. O score não penaliza alavancagem excessiva.

#### EV/EBITDA — 5.3% de cobertura (888 ações sem dado)

Indicador de **valuation relativo** — mede se a empresa está cara ou barata em relação à sua geração de caixa operacional. Sem ele, o sistema não consegue identificar empresas sobrevalorizadas.

#### P/L e P/VP — ~30% de cobertura

Indicadores básicos de valuation. Com 70% das ações sem P/L, o sistema não consegue avaliar se o preço de mercado é justo em relação ao lucro ou ao patrimônio.

#### CAGR de Lucro — 29.5% de cobertura

Sem histórico de crescimento, o sistema não distingue empresas em expansão de empresas em declínio.

---

### 10.3 Evidências de Viés nos Scores

#### Ações "Excelente" sem dados de valuation

Observando o Top 20 de ações (seção 5), **nenhuma das 26 ações "Excelente" tem P/L preenchido**. Isso significa que o score alto foi construído principalmente sobre ROE elevado + DY elevado + CAGR de lucro — sem qualquer avaliação de se o preço de mercado é justo.

Uma empresa pode ter ROE de 180% e DY de 80% e ainda assim estar **extremamente sobrevalorizada** — e o sistema atual classificaria como "Excelente".

#### FIIs com scores inflados por P/VP ausente

53.3% dos FIIs são classificados como "Excelente". O P/VP — indicador mais importante para FIIs (peso 30%) — está ausente em **80.6% dos FIIs**. Isso significa que o score "Excelente" de muitos FIIs ignora completamente se a cota está sendo negociada com prêmio ou desconto sobre o patrimônio.

#### Score mínimo artificialmente alto

O score mínimo observado é **18.3** (não zero). Isso ocorre porque mesmo empresas com todos os indicadores negativos recebem score neutro (50) nos indicadores ausentes, elevando o piso artificialmente.

---

### 10.4 Comparação: Projeto Analítico vs Projeto Educacional

| Critério | Projeto Analítico | Projeto Educacional |
|---|---|---|
| **Precisão dos scores** | Requer dados reais em ≥ 5/7 indicadores | Scores estimados são aceitáveis como exemplo |
| **Dívida/EBITDA** | Obrigatório — risco financeiro crítico | Pode ser omitido com aviso |
| **Responsabilidade** | Alta — usuário pode tomar decisões financeiras | Baixa — contexto de aprendizado |
| **Disclaimer** | Insuficiente apenas no texto | Suficiente com disclaimer claro |
| **Cobertura atual** | ❌ Insuficiente (55%+ estimado) | ✅ Aceitável com transparência |
| **Fontes gratuitas** | ❌ Limitadas para dados completos | ✅ Adequadas para fins didáticos |

---

### 10.5 Caminhos Possíveis

#### Opção A — Manter como projeto educacional (menor esforço)

- Adicionar aviso explícito no frontend: *"Score baseado em X/7 indicadores reais. Indicadores ausentes usam valor estimado neutro."*
- Exibir o `available_indicators` de forma proeminente em cada análise
- Reforçar o disclaimer: *"Esta análise é educacional e não deve ser usada como base para decisões de investimento"*
- **Não requer mudanças no backend**

#### Opção B — Melhorar cobertura com fontes alternativas (esforço médio)

- Integrar **API da CVM** (dados oficiais de DRE e balanço) para calcular Dívida/EBITDA real
- Usar **dados do Banco Central** para indicadores macroeconômicos setoriais
- Calcular P/VP de FIIs via `current_price / book_value_per_share` quando disponível
- **Estimativa:** +2 a 4 semanas de desenvolvimento

#### Opção C — Integrar fonte paga (maior esforço, maior qualidade)

- APIs como **Economatica**, **Refinitiv** ou **Bloomberg** fornecem dados completos
- Cobertura próxima de 100% para todos os indicadores
- **Estimativa:** custo mensal + 1 a 2 semanas de integração

---

### 10.6 Recomendação para Discussão do Time

> **Pergunta central:** O FundamentAI deve ser posicionado como ferramenta analítica ou educacional?

**Argumentos para educacional:**
- As fontes gratuitas disponíveis (fundamentus + yfinance) têm limitações estruturais que não são contornáveis sem custo
- O projeto já tem valor educacional significativo: explica indicadores, mostra como calcular scores, demonstra o fluxo completo de dados
- Manter o escopo educacional é honesto com o usuário e evita responsabilidade por decisões financeiras baseadas em dados incompletos

**Argumentos para analítico (com melhorias):**
- A Opção B (API da CVM) é viável e gratuita — os dados de DRE e balanço são públicos
- FIIs têm cobertura razoável (DY 80%, CAGR 90%) e poderiam ser o foco inicial
- Um subconjunto de ~200 ações com boa cobertura poderia ser o escopo analítico inicial

**Sugestão:** definir o posicionamento antes de iniciar o frontend, pois impacta diretamente como os scores e avisos serão apresentados ao usuário.

---

> *Análise elaborada com base nos dados do banco em 2026-05-17. Para atualizar os números: `python -m backend.scripts.generate_report`*