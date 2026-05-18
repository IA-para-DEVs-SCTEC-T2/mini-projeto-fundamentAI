# Compliance e Governança de Dados

Diretrizes de conformidade, rastreabilidade e qualidade de dados do FundamentAI.
Este arquivo fornece contexto permanente ao agente Kiro sobre as regras de compliance do projeto.

---

## Disclaimer Obrigatório

**Todo output do sistema deve incluir o disclaimer:**

> "Esta análise é informativa e baseada em dados históricos públicos. Não constitui recomendação de investimento. A decisão final é sempre do usuário."

- O disclaimer deve aparecer em **toda análise gerada pela LLM**
- Deve estar visível no frontend em todas as páginas de análise
- Nunca omitir ou encurtar o disclaimer em respostas da API

---

## Fontes de Dados — Conformidade de Uso

| Fonte | Tipo de uso permitido | Restrições |
|---|---|---|
| **yfinance** | Dados públicos para uso educativo e pessoal | Não usar para sistemas comerciais de alta frequência; respeitar rate limits |
| **fundamentus** | Scraping de dados públicos da B3 | Uso moderado; não sobrecarregar o servidor; delay entre requisições |
| **API BCB (SGS)** | API pública oficial do Banco Central | Sem restrições para uso público; respeitar timeout de 10s |

**Regras de coleta:**
- Delay mínimo de 0.2s entre requisições ao fundamentus
- Timeout de 10s para API do BCB
- Nunca armazenar dados brutos de fontes com restrição de redistribuição
- Dados são coletados apenas para processamento interno — não redistribuídos diretamente

---

## Rastreabilidade das Fontes

Cada dado persistido no banco deve ter rastreabilidade de origem:

| Campo | Tabela | Fonte |
|---|---|---|
| `current_price`, `pe_ratio`, `pb_ratio` (ações) | `financial_data`, `indicators` | fundamentus |
| `current_price`, `pb_ratio`, `dividend_yield` (FIIs) | `financial_data`, `indicators` | yfinance |
| `net_income_growth_yoy`, `revenue_growth_yoy` | `indicators` | yfinance (DRE histórico) |
| `selic_rate`, `ipca_12m` | Contexto de prompt (não persistido) | API BCB |
| `score`, `score_label` | `indicators` | Cálculo interno |
| `verdict`, `conclusion` | `analyses` | Anthropic Claude |

**Metadados obrigatórios em `analyses`:**
- `model_used`: modelo Claude utilizado
- `prompt_version`: versão do template de prompt
- `generated_at`: timestamp da geração

---

## Política de Retenção de Dados

| Tabela | Retenção | Justificativa |
|---|---|---|
| `tickers` | Indefinida | Cadastro de referência |
| `inactive_tickers` | 1 ano após última verificação | Revisão periódica de inativos |
| `financial_data` | 2 anos de histórico | Análise de tendências |
| `indicators` | 2 anos de histórico | Comparação histórica de scores |
| `analyses` | 1 ano | Cache de análises LLM |

**Limpeza periódica:** executar trimestralmente via script de manutenção.

---

## Qualidade dos Dados — Regras de Validação

### Score Neutro para Indicadores Ausentes — Metodologia Explícita

> ⚠️ **Esta seção documenta uma decisão de design com impacto direto na confiabilidade dos scores. Deve ser comunicada ao usuário final.**

Quando um indicador está **ausente (nulo)** no banco — seja por limitação da fonte, por não ter sido coletado ainda, ou por ter sido removido pela validação de range — o sistema **não descarta o ticker**. Em vez disso, atribui um **score neutro de 50 pontos (em escala 0–100)** para aquele componente no cálculo do score final.

#### Justificativa

- Descartar tickers com dados incompletos eliminaria a maioria dos ativos da B3 (cobertura de P/L é ~30%, EV/EBITDA ~5%)
- O score neutro representa "sem informação suficiente para penalizar ou premiar"
- É preferível a um score artificialmente baixo por ausência de dado

#### Impacto por indicador ausente — Ações

| Indicador ausente | Peso no score | Score neutro aplicado | Impacto no score final |
|---|---|---|---|
| ROE | 20% | 50 pts | +10 pts (neutro) |
| Margem Líquida | 15% | 50 pts | +7.5 pts (neutro) |
| Dívida/EBITDA | 15% | 50 pts | +7.5 pts (neutro) |
| P/L | 15% | 50 pts | +7.5 pts (neutro) |
| CAGR Lucro | 15% | 50 pts | +7.5 pts (neutro) |
| EV/EBITDA | 10% | 50 pts | +5 pts (neutro) |
| Dividend Yield | 10% | 50 pts | +5 pts (neutro) |

> Um ticker de ação **sem nenhum indicador** recebe score final = **50.0 (Bom)** — inteiramente composto por scores neutros.

#### Impacto por indicador ausente — FIIs

| Indicador ausente | Peso no score | Score neutro aplicado | Impacto no score final |
|---|---|---|---|
| Dividend Yield | 35% | 50 pts | +17.5 pts (neutro) |
| P/VP | 30% | 50 pts | +15 pts (neutro) |
| CAGR Dividendos | 20% | 50 pts | +10 pts (neutro) |
| P/L | 15% | 50 pts | +7.5 pts (neutro) |

> Um FII **sem nenhum indicador** recebe score final = **50.0 (Bom)** — inteiramente composto por scores neutros.

#### Cobertura atual do banco (referência: 2026-05-17)

| Tipo | Indicador | Cobertura | Tickers com score neutro nesse componente |
|---|---|---|---|
| Ação | ROE | 82.8% | ~161 ações |
| Ação | Margem Líquida | 54.5% | ~427 ações |
| Ação | P/L | 30.2% | ~655 ações |
| Ação | P/VP | 29.6% | ~660 ações |
| Ação | EV/EBITDA | 5.3% | ~888 ações |
| Ação | Dívida/EBITDA | 0.0% | **938 ações** (100%) |
| Ação | CAGR Lucro | 29.5% | ~661 ações |
| FII | P/VP | 19.4% | ~145 FIIs |
| FII | P/L | 60.0% | ~72 FIIs |
| FII | Dividend Yield | 80.0% | ~36 FIIs |
| FII | CAGR Dividendos | 90.0% | ~18 FIIs |

#### Obrigações de transparência

1. **API:** o campo `available_indicators` no response do score lista quais indicadores foram efetivamente usados (não neutros)
2. **Frontend:** deve exibir o número de indicadores disponíveis junto ao score (ex: "Score baseado em 4/7 indicadores")
3. **LLM:** o prompt deve informar ao Claude quais indicadores estão ausentes, para que a análise textual reflita essa limitação
4. **Relatório:** `backend/reports/relatorio_banco.md` documenta a cobertura atual por indicador

#### Implementação

O score neutro é aplicado em `backend/processors/scoring.py`:

```python
# Exemplo: _score_pe_ratio retorna 50.0 quando pe_ratio é None
def _score_pe_ratio(pe_ratio: Optional[float]) -> float:
    if pe_ratio is None:
        return 50.0  # score neutro — dado ausente
    ...
```

Cada função de score individual (`_score_roe`, `_score_net_margin`, etc.) segue o mesmo padrão: retorna `50.0` quando o valor é `None`.

---

### Indicadores de ações (ranges esperados)

| Indicador | Range válido | Ação se fora do range |
|---|---|---|
| ROE | -5.0 a 5.0 (decimal) | Log de anomalia; não persistir |
| Margem Líquida | -2.0 a 1.0 | Log de anomalia; não persistir |
| P/L | -500 a 500 | Aceitar negativo (prejuízo); log se > 500 |
| P/VP | 0 a 100 | Log se > 50 |
| Dívida/EBITDA | -50 a 50 | Log se fora do range |
| EV/EBITDA | 0 a 200 | Log se > 100 |
| Dividend Yield | 0 a 1.0 (decimal) | Log se > 0.5 (50%) |

### Indicadores de FIIs (ranges esperados)

| Indicador | Range válido | Ação se fora do range |
|---|---|---|
| P/VP | 0 a 10 | Log se > 5 |
| P/L | 0 a 100 | Log se > 50 |
| Dividend Yield | 0 a 1.0 (decimal) | Log se > 0.5 (50%) |
| Crescimento DY | -1.0 a 5.0 | Log se fora do range |

### Regra de mínimo de indicadores
- Todo ticker ativo deve ter **≥ 3 indicadores** disponíveis
- Verificação automática após cada ETL via `ensure_min_indicators.py`
- Tickers que não atingirem o mínimo são movidos para `inactive_tickers`

---

## Auditoria e Monitoramento

### Logs obrigatórios
- Toda coleta de dados (fonte, ticker, timestamp)
- Erros de API com código de status e mensagem
- Tickers movidos para inativos (motivo e data)
- Scores calculados com número de indicadores disponíveis
- Análises geradas pela LLM (modelo, tokens, latência)

### Relatórios automáticos

Todos os relatórios são gerados em `backend/reports/`:

| Arquivo | Gerado quando | Conteúdo |
|---|---|---|
| `banco_analise_nulos.csv` | Após cada `populate_all_tickers` | Campos nulos por ticker |
| `relatorio_inativos.csv` | Após cada `populate_all_tickers` | Tickers inativos com motivo e tipo |
| `relatorio_anomalias.csv` | Quando anomalias são detectadas | Indicadores fora do range por ticker |
| `relatorio_banco.md` | Sob demanda via `generate_report.py` | Visão completa: scores, cobertura de indicadores, top/bottom tickers |

> Os CSVs não são versionados no Git (`.gitignore`). A pasta `backend/reports/` é mantida via `.gitkeep`.

---

## Segurança

- `ANTHROPIC_API_KEY` nunca no código — sempre via variável de ambiente
- Arquivo `.env` no `.gitignore` — nunca versionado
- Banco SQLite local não versionado (`*.db` no `.gitignore`)
- Logs de prompt não devem conter chaves de API ou senhas

---

## Contexto para o Agente Kiro

Ao trabalhar neste projeto:

1. **Sempre incluir o disclaimer** em análises geradas pela LLM
2. **Respeitar os delays** entre requisições às fontes externas
3. **Não redistribuir dados brutos** das fontes — apenas dados processados
4. **Validar ranges** antes de persistir indicadores no banco
5. **Registrar a fonte** de cada dado coletado nos logs
6. **Nunca expor** chaves de API, senhas ou tokens em código ou logs
7. **Score neutro é intencional** — indicadores nulos recebem 50 pts por design; nunca remover essa lógica sem documentar o impacto
8. **Transparência obrigatória** — o campo `available_indicators` no response do score deve sempre refletir quais indicadores foram realmente usados (não neutros); o frontend deve exibir essa informação ao usuário
