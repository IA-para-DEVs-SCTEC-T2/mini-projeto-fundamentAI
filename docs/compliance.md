# Compliance e Governança de Dados — FundamentAI

## Visão Geral

Este documento define as diretrizes de conformidade, rastreabilidade e qualidade de dados do FundamentAI. Aplica-se a todos os dados coletados, processados, armazenados e exibidos pela plataforma.

---

## 1. Disclaimer e Limites de Responsabilidade

### Disclaimer obrigatório

Todo output do sistema inclui obrigatoriamente:

> *"Esta análise é informativa e baseada em dados históricos públicos. Não constitui recomendação de investimento. A decisão final é sempre do usuário."*

### Limites de responsabilidade

- O FundamentAI **não é uma plataforma de investimentos** e não possui licença para oferecer consultoria financeira
- As análises são geradas por modelos de linguagem (LLM) com base em dados históricos — podem conter imprecisões
- Dados de mercado têm defasagem de pelo menos 1 dia útil (processamento pós-fechamento)
- O sistema não garante a completude ou exatidão dos dados fornecidos pelas fontes externas
- Decisões de investimento baseadas nas análises são de **exclusiva responsabilidade do usuário**

---

## 2. Conformidade com Uso das Fontes de Dados

### 2.1 yfinance

| Item | Detalhe |
|---|---|
| Tipo | Biblioteca Python que acessa dados públicos do Yahoo Finance |
| Uso permitido | Educativo, pesquisa, uso pessoal |
| Restrições | Não usar para sistemas comerciais de alta frequência; respeitar rate limits |
| Implementação | Delay implícito via processamento sequencial; sem paralelismo agressivo |

### 2.2 fundamentus

| Item | Detalhe |
|---|---|
| Tipo | Scraping de dados públicos da B3 via biblioteca Python |
| Uso permitido | Consulta de indicadores fundamentalistas públicos |
| Restrições | Uso moderado; não sobrecarregar o servidor |
| Implementação | Delay mínimo de **0.2s** entre requisições no ETL |

### 2.3 API do Banco Central (BCB/SGS)

| Item | Detalhe |
|---|---|
| Tipo | API pública oficial do Banco Central do Brasil |
| Uso permitido | Irrestrito para uso público |
| Restrições | Respeitar timeout de 10s; não fazer polling excessivo |
| Implementação | Timeout configurado em `_REQUEST_TIMEOUT = 10` no coletor |

### 2.4 Anthropic API (Claude)

| Item | Detalhe |
|---|---|
| Tipo | API comercial de LLM |
| Uso permitido | Geração de análises textuais estruturadas |
| Restrições | Chave de API nunca no código; respeitar rate limits |
| Implementação | `ANTHROPIC_API_KEY` via variável de ambiente; tratamento de `RateLimitError` |

---

## 3. Rastreabilidade das Fontes de Dados

Cada dado persistido no banco tem origem rastreável:

| Dado | Tabela | Fonte | Frequência |
|---|---|---|---|
| Cotação, P/L, P/VP, ROE, Margem (ações) | `financial_data`, `indicators` | fundamentus | Diária |
| Cotação, P/VP, DY, dividendos (FIIs) | `financial_data`, `indicators` | yfinance | Diária |
| Histórico de preços | Não persistido (retornado na API) | yfinance | Por consulta |
| CAGR de lucro e receita | `indicators` | yfinance (DRE histórico) | Semanal |
| SELIC, IPCA | Contexto de prompt (não persistido) | API BCB | Por análise |
| Score, score_label | `indicators` | Cálculo interno | Diária |
| Veredito, conclusão, explicações | `analyses` | Anthropic Claude | Por consulta |

### Metadados de rastreabilidade em `analyses`

```
model_used      → modelo Claude utilizado (ex: claude-sonnet-4-5)
prompt_version  → versão do template de prompt (ex: 1.0.0)
generated_at    → timestamp UTC da geração
```

---

## 4. Política de Retenção de Dados

| Tabela | Período de retenção | Justificativa |
|---|---|---|
| `tickers` | Indefinida | Cadastro de referência permanente |
| `inactive_tickers` | 1 ano após `last_checked_at` | Revisão periódica; pode reativar |
| `financial_data` | 2 anos de histórico | Análise de tendências e comparação |
| `indicators` | 2 anos de histórico | Histórico de scores e indicadores |
| `analyses` | 1 ano | Cache de análises LLM; custo de regeneração |

### Limpeza periódica

Executar trimestralmente:

```bash
python -m backend.scripts.data_retention_cleanup
```

O script remove registros mais antigos que os períodos definidos acima, preservando sempre o registro mais recente por ticker.

---

## 5. Qualidade dos Dados — Validação de Ranges

O módulo `backend/processors/data_validator.py` valida indicadores antes da persistência.

### Ranges válidos — Ações

| Indicador | Mínimo | Máximo | Ação se fora do range |
|---|---|---|---|
| ROE | -5.0 | 5.0 | Log de anomalia; não persistir |
| Margem Líquida | -2.0 | 1.0 | Log de anomalia; não persistir |
| P/L | -500 | 500 | Log se \|P/L\| > 500 |
| P/VP | 0 | 100 | Log se > 50 |
| Dívida/EBITDA | -50 | 50 | Log se fora do range |
| EV/EBITDA | 0 | 200 | Log se > 100 |
| Dividend Yield | 0 | 1.0 | Log se > 0.5 (50%) |
| Crescimento Lucro | -1.0 | 10.0 | Log se fora do range |

### Ranges válidos — FIIs

| Indicador | Mínimo | Máximo | Ação se fora do range |
|---|---|---|---|
| P/VP | 0 | 10 | Log se > 5 |
| P/L | 0 | 100 | Log se > 50 |
| Dividend Yield | 0 | 1.0 | Log se > 0.5 (50%) |
| Crescimento DY | -1.0 | 5.0 | Log se fora do range |

---

## 6. Auditoria e Monitoramento

### Logs obrigatórios (implementados)

- Toda coleta de dados: fonte, ticker, timestamp, status
- Erros de API: código HTTP, mensagem, ticker afetado
- Tickers movidos para inativos: motivo e data
- Scores calculados: valor, label, número de indicadores disponíveis
- Análises LLM: modelo, tokens consumidos, latência

### Relatórios automáticos

Todos os relatórios são gerados em `backend/reports/`:

| Arquivo | Gerado quando | Conteúdo |
|---|---|---|
| `banco_analise_nulos.csv` | Após cada `populate_all_tickers` | Campos nulos por ticker |
| `relatorio_inativos.csv` | Após cada `populate_all_tickers` | Tickers inativos com motivo e tipo |
| `relatorio_anomalias.csv` | Quando anomalias são detectadas | Indicadores fora do range por ticker |

> Os CSVs não são versionados no Git. A pasta `backend/reports/` é mantida via `.gitkeep`.

### Verificação de qualidade pós-ETL

O script `ensure_min_indicators.py` é executado automaticamente após cada ETL e garante que todos os tickers ativos tenham ≥ 3 indicadores disponíveis.

---

## 7. Segurança de Dados

| Prática | Implementação |
|---|---|
| Chaves de API fora do código | `ANTHROPIC_API_KEY` via `.env` (no `.gitignore`) |
| Banco local não versionado | `*.db` no `.gitignore` |
| Sem dados sensíveis de usuário | MVP não coleta dados pessoais |
| Logs sem segredos | Scripts de logging filtram variáveis de ambiente |

---

## 8. Evolução Futura

Quando carteiras de usuário forem implementadas:

- Autenticação via JWT
- Senhas com bcrypt (nunca em texto plano)
- Dados de carteira criptografados em repouso
- Conformidade com LGPD (Lei Geral de Proteção de Dados)
- Política de exclusão de dados a pedido do usuário

---

*Documento mantido em `.kiro/steering/compliance.md` (contexto do agente) e `docs/compliance.md` (referência da equipe).*
