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
