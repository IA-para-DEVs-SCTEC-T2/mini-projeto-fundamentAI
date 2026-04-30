# Stack Tecnológica

Definição das tecnologias utilizadas no projeto, baseada no README. Onde a tecnologia específica não foi explicitada, a escolha é indicada como inferência.

---

## Backend

| Tecnologia | Papel |
|---|---|
| **Python** | Linguagem principal do backend |
| **yfinance** | Coleta de dados financeiros (cotações, demonstrativos) |
| **fundamentus** | Coleta de indicadores fundamentalistas da B3 |
| **API do Banco Central** | Dados macroeconômicos: SELIC e IPCA |
| **Anthropic API** | Geração das análises via LLM (modelos Claude) |
| **FastAPI** | Framework leve e performático para expor a API REST ao frontend; padrão moderno em projetos Python com foco em dados |
| **SQLite / PostgreSQL** | Banco de dados para persistência dos dados processados; SQLite para desenvolvimento local, PostgreSQL para produção |
| **SQLAlchemy** | ORM para abstração do banco de dados, compatível com ambos os bancos acima |
| **APScheduler ou Cron** | Agendamento do ETL diário pós-fechamento do mercado |
| **pandas** | Manipulação e processamento de dados tabulares financeiros |

---

## Geração de Análises via LLM (Anthropic)

Os dados coletados e processados são injetados em prompts estruturados e enviados à API da Anthropic para geração do conteúdo exibido ao usuário.

### Modelos utilizados

| Modelo | Uso indicado |
|---|---|
| `claude-sonnet-4-5` | Análises completas — maior qualidade de raciocínio |
| `claude-haiku-4-5` | Respostas rápidas ou consultas de menor complexidade |

> A escolha do modelo por chamada pode ser parametrizada conforme o tipo de análise solicitada.

### Fluxo de geração

```
Dados financeiros processados (indicadores, macro, histórico)
        ↓
backend/prompts/builder.py  → monta o prompt estruturado
        ↓
Anthropic API (Claude)      → gera a análise em formato estruturado
        ↓
backend/api/                → retorna o resultado ao frontend
        ↓
frontend/                   → renderiza veredito, score e explicações
```

### Formato de resposta

O prompt define explicitamente o formato de saída esperado (ex: JSON estruturado) para garantir:

- Parsing confiável no backend antes de repassar ao frontend
- Separação clara entre campos: veredito, score, pontos positivos/negativos, explicação de indicadores, nível de confiança
- Renderização consistente na UI sem tratamento ad-hoc de texto livre

### Boas práticas

- Prompts versionados em `backend/prompts/` — nunca hardcoded nas rotas da API
- Separar o template do prompt da lógica de injeção de dados
- Tratar erros e timeouts da API da Anthropic com fallback adequado
- Não expor a chave da API (`ANTHROPIC_API_KEY`) no código — usar variável de ambiente

---

## Frontend

| Tecnologia | Papel |
|---|---|
| **React** | Framework principal do frontend |
| **Recharts ou Chart.js** | Biblioteca de gráficos compatível com React, necessária para os dashboards de análise |
| **Axios** | Cliente HTTP para chamadas à API do backend |
| **React Router** | Navegação entre páginas (Home e Analysis) |

---

## Fontes de Dados Externas

| Fonte | Dados fornecidos |
|---|---|
| `yfinance` | Cotações, histórico de preços, demonstrativos financeiros |
| `fundamentus` | Indicadores fundamentalistas (ROE, ROIC, P/L, P/VP, etc.) |
| API Banco Central (BCB) | SELIC e IPCA |
| API oficial da B3 | Possível expansão futura — fora do escopo inicial |

---

## Fluxo de Dados

```
Fontes externas (yfinance, fundamentus, BCB)
        ↓
backend/collectors/     → coleta bruta por fonte
        ↓
backend/processors/     → cálculo de indicadores e scoring
        ↓
Banco de dados          → persistência dos dados processados
        ↓
backend/prompts/        → montagem do prompt estruturado com os dados
        ↓
Anthropic API (Claude)  → geração da análise em formato estruturado
        ↓
backend/api/            → exposição via REST ao frontend
        ↓
frontend/               → dashboard, gráficos e veredito
```

---

## Restrições e Decisões Técnicas

- **Sem dados em tempo real no MVP** — processamento diário pós-fechamento do mercado
- **Dados públicos apenas** — nenhuma fonte paga ou proprietária no escopo inicial
- **Análise fundamentalista exclusivamente** — sem análise técnica/gráfica
- **Segurança:** caso carteiras de usuário sejam implementadas, exige criptografia no armazenamento e boas práticas de autenticação (ex: JWT + bcrypt)

---

## IDE e Ambiente de Desenvolvimento

Utilizar o **[Kiro](https://kiro.dev)** como IDE, no modo **Auto**.

- O modo **Auto** permite que o agente execute alterações de forma autônoma no workspace
- Os arquivos em `.kiro/steering/` fornecem contexto permanente do projeto ao agente em todas as interações
- Não utilizar outros modos (Supervised) como padrão — reservar para situações que exijam revisão manual de cada alteração
