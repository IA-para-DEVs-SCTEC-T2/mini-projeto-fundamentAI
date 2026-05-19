# 📊 FundamentAI - Analisador Fundamentalista de Ações da B3

---

## 📌 Visão Geral

Este projeto tem como objetivo ajudar investidores iniciantes a analisar empresas listadas na B3 de forma fundamentada em dados, com foco em segurança e rentabilidade no longo prazo.

A solução agrega dados públicos de diferentes fontes, processa indicadores fundamentalistas e gera análises estruturadas para facilitar a tomada de decisão — com um viés educativo e explicativo.

> ⚠️ **Disclaimer:** Este projeto não fornece recomendações de investimento. As análises são informativas e baseadas em dados históricos. A decisão final é sempre do usuário.

---

## ❗ Problema

Investidores iniciantes enfrentam diversas dificuldades:

- Grande volume de informações dispersas
- Necessidade de interpretar indicadores financeiros complexos
- Alto custo de consultorias especializadas
- Tempo elevado para análise de empresas
- Falta de padronização na avaliação de ativos

---

## 💡 Solução

Criar uma plataforma que:

- Consolida dados financeiros de múltiplas fontes confiáveis
- Aplica critérios objetivos de análise fundamentalista
- Gera um veredito estruturado sobre o ativo
- Explica os indicadores de forma acessível
- Apresenta dados comparativos com setor/mercado
- Entrega uma experiência visual com gráficos e scores

---

## 🎯 Objetivos

- Auxiliar na análise de ações e FIIs da B3
- Reduzir a barreira de entrada para novos investidores
- Fornecer insumos claros para tomada de decisão
- Servir como ferramenta educativa

---

## 🧠 Critérios de Análise (Baseados em Dados)

O sistema aplica indicadores **específicos por tipo de ativo**, mas entrega um **output unificado** para ações e FIIs — garantindo consistência no frontend.

### 📈 Para Ações (Empresas da B3)

Foco em eficiência operacional, lucratividade e endividamento.

| Indicador | Descrição | Peso no Score |
|---|---|---|
| P/L | Quanto o mercado paga por R$1 de lucro | 15% |
| ROE | Retorno sobre Patrimônio Líquido | 20% |
| Dívida Líquida / EBITDA | Nível de alavancagem financeira | 15% |
| Margem Líquida | Eficiência na geração de lucro | 15% |
| EV/EBITDA | Valor da empresa sobre geração de caixa | 10% |
| Dividend Yield | Rendimento distribuído / preço | 10% |
| Crescimento Lucro YoY | CAGR do lucro líquido (histórico 5 anos) | 15% |

**Fonte:** fundamentus (principal) + yfinance (histórico DRE)

### 🏢 Para FIIs (Fundos de Investimento Imobiliário)

Foco em geração de renda e valor dos ativos.

| Indicador | Descrição | Peso no Score |
|---|---|---|
| P/VP | Desconto ou prêmio sobre o patrimônio | 30% |
| P/L | Preço sobre rendimento | 15% |
| Dividend Yield | Rendimento distribuído / preço da cota | 35% |
| Crescimento Dividendos YoY | CAGR dos dividendos anuais | 20% |

**Fonte:** yfinance (exclusivo)

### 🏆 Score Fundamentalista (Output Unificado)

| Score | Classificação |
|---|---|
| 75 – 100 | Excelente |
| 50 – 74 | Bom |
| 25 – 49 | Regular |
| 0 – 24 | Fraco |

### 🏦 Dados Macroeconômicos

Injetados no contexto de análise da LLM:

- **SELIC** — taxa básica de juros (BCB/SGS série 11)
- **IPCA** — inflação acumulada 12 meses (BCB/SGS série 433)

---

## ⚙️ Arquitetura

### 🔧 Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python + FastAPI |
| Frontend | React + Vite |
| Gráficos | Recharts |
| Geração de análises | Anthropic API (Claude) |

### 🔄 Fluxo de Funcionamento

```
Coleta de dados via Python (yfinance, fundamentus, BCB)
        ↓
Processamento e padronização dos indicadores
        ↓
Armazenamento em banco de dados
        ↓
Geração de prompt estruturado com os dados processados
        ↓
Envio à API da Anthropic (Claude Sonnet / Haiku)
        ↓
Retorno em formato estruturado otimizado para renderização no frontend
```

### 🔌 Fontes de Dados

| Fonte | Tipo de Ativo | Dados fornecidos |
|---|---|---|
| `fundamentus` | Ações | P/L, P/VP, ROE, ROIC, Margem, EV/EBITDA, DY, balanço |
| `yfinance` | Ações + FIIs | Cotações, histórico de preços, DRE histórico, dados de FIIs |
| API Banco Central | Ambos | SELIC e IPCA |

> **FIIs:** fundamentus não suporta FIIs. yfinance é a fonte exclusiva para fundos imobiliários.

---

## 🧾 Estrutura do Prompt

O sistema utiliza prompts estruturados enviados à **API da Anthropic (Claude)** contendo:

- Dados financeiros confiáveis coletados de fontes públicas
- Indicadores calculados (ROE, ROIC, P/L, P/VP, etc.)
- Contexto macroeconômico (SELIC, IPCA)
- Regras de análise e critérios de avaliação

O prompt define explicitamente o **formato de saída** (estruturado) para garantir parsing confiável e renderização consistente na UI.

**Modelos utilizados:**
- `claude-sonnet-4-5` — análises completas, maior qualidade de raciocínio
- `claude-haiku-4-5` — consultas rápidas ou de menor complexidade

**Saída esperada:**

- Veredito sobre o ativo
- Explicação dos indicadores
- Avaliação de risco
- Sugestão de momento *(não recomendação)*

---

## �️ Banco de Dados

O sistema usa **SQLite** em desenvolvimento e **PostgreSQL** em produção, gerenciado via SQLAlchemy.

### Tabelas

| Tabela | Descrição |
|---|---|
| `tickers` | Ativos ativos (ações e FIIs) com tipo e setor |
| `inactive_tickers` | Tickers inativos — excluídos da análise |
| `financial_data` | Dados financeiros brutos por data de referência |
| `indicators` | Indicadores calculados por data de referência |
| `analyses` | Análises geradas pela LLM |

### Campo `asset_type`

Presente em `tickers` e `inactive_tickers`. Identifica o tipo do ativo:

| Valor | Tipo |
|---|---|
| `"stock"` | Ação (empresa da B3) |
| `"fii"` | Fundo de Investimento Imobiliário |

A classificação é automática: tickers terminados em `11` são FIIs (ex: HGLG11), os demais são ações.

### Popular o banco

```bash
# Popula com todos os ~993 tickers da B3 (retoma de onde parou)
python -m backend.scripts.populate_all_tickers

# Atualiza CAGR de lucro via yfinance (ações)
python -m backend.scripts.update_income_growth

# Verifica e enriquece tickers com < 3 indicadores (executado automaticamente pelo ETL)
python -m backend.scripts.ensure_min_indicators

# Limpeza trimestral conforme política de retenção de dados
python -m backend.scripts.data_retention_cleanup --dry-run  # apenas relatório
python -m backend.scripts.data_retention_cleanup            # executa limpeza
```

Os relatórios são gerados automaticamente em `backend/reports/` (não versionados no Git):

| Arquivo | Conteúdo |
|---|---|
| `banco_analise_nulos.csv` | Campos nulos por ticker |
| `relatorio_inativos.csv` | Tickers inativos com motivo e tipo |
| `relatorio_anomalias.csv` | Indicadores fora do range (compliance) |

#### Garantia de qualidade de dados

O script `ensure_min_indicators` é executado automaticamente ao final de cada rodada do ETL. Ele garante que todos os tickers ativos tenham pelo menos **3 indicadores disponíveis** para o cálculo do score.

**Fluxo por ticker com < 3 indicadores:**
1. Busca indicadores faltantes em fonte alternativa (yfinance)
2. Calcula indicadores derivados a partir dos dados já no banco (ex: ROE = lucro/patrimônio)
3. Se ainda < 3 após todas as tentativas → move para `inactive_tickers`

```bash
# Apenas relatório, sem alterar banco
python -m backend.scripts.ensure_min_indicators --dry-run
```

---



- Consulta por ticker — ações e FIIs da B3 (~937 ativos ativos)
- Score fundamentalista unificado (0-100) com classificação qualitativa
- Indicadores específicos por tipo de ativo (ações vs FIIs)
- Visualização de gráficos e histórico de preços
- Comparação setorial
- Análise gerada por LLM (Claude) com explicações educativas
- Identificação de tickers inativos com mensagem explicativa
- Atualização diária (pós-fechamento do mercado, 19h Brasília)

---

## 🔐 Segurança e Privacidade

- Dados utilizados são públicos
- Avaliar necessidade de cadastro de carteira do usuário
  - Caso implementado:
    - Armazenamento seguro (criptografia)
    - Boas práticas de autenticação

---

## 📦 Escopo Inicial (MVP)

- Ações e FIIs ativos listados na B3
- Análise fundamentalista com indicadores específicos por tipo de ativo
- Score unificado (0-100) — mesmo output para ações e FIIs
- Dados históricos (não tempo real)
- Sem recomendação direta de compra/venda
- Tickers inativos identificados e bloqueados com mensagem ao usuário

---

## 🚀 Diferenciais

- Agregação de múltiplas fontes em um único lugar
- Padronização da análise
- UX simplificada para iniciantes
- Explicação educativa dos dados
- Escalável para outros mercados e ativos

---

## 📊 Possíveis Evoluções

- Inclusão de outros mercados (ex: EUA)
- Criação de carteiras personalizadas
- Alertas inteligentes
- Integração com dados em tempo real
- Machine Learning para scoring avançado

---

## 🛠️ Ambiente de Desenvolvimento

Este projeto utiliza o **[Kiro](https://kiro.dev)** como IDE, no modo **Auto**.

O Kiro é uma IDE com IA integrada que permite desenvolvimento assistido com contexto completo do projeto. O modo **Auto** permite que o agente execute alterações de forma autônoma no workspace, acelerando o desenvolvimento.

Os arquivos de steering em `.kiro/steering/` definem o contexto permanente injetado em todas as interações com o Kiro:

| Arquivo | Conteúdo |
|---|---|
| `product.md` | Visão do produto, problema, público-alvo e escopo |
| `structure.md` | Organização de diretórios e convenções de código |
| `tech.md` | Stack tecnológica e decisões de arquitetura |
| `gitflow.md` | Fluxo de versionamento Git e convenções de commits |

---

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Node.js 18+ e npm (para o frontend)
- Git

### 1️⃣ Clonar o Repositório

```bash
git clone https://github.com/IA-para-DEVs-SCTEC-T2/FundamentAI.git
cd FundamentAI
```

### 2️⃣ Configurar Backend

#### Instalar Dependências

Use sempre um ambiente virtual para isolar as dependências do projeto:

```bash
# Na raiz do projeto: mini-projeto-equipe08/

# Criar ambiente virtual dentro de backend/
python -m venv backend/venv

# Ativar ambiente virtual
source backend/venv/bin/activate  # macOS/Linux
# backend\venv\Scripts\activate   # Windows

# Instalar dependências
pip install -r backend/requirements.txt
```

#### Configurar Variáveis de Ambiente

1. Copiar o arquivo de exemplo:
   ```bash
   cp .env.example .env
   ```

2. Editar `.env` e preencher as variáveis necessárias:
   ```bash
   # Obrigatório: chave da API da Anthropic
   ANTHROPIC_API_KEY=sua_chave_aqui
   
   # Opcional: ajustar configurações de banco e API
   DATABASE_URL=sqlite:///./fundamentai.db
   API_PORT=8000
   ```

3. **Obter chave da Anthropic:**
   - Criar conta em [console.anthropic.com](https://console.anthropic.com)
   - Gerar API key em "API Keys"
   - Copiar e colar no arquivo `.env`

#### Verificar Instalação

```bash
# Testar importações (da raiz do projeto, com venv ativo)
python -c "import fastapi, anthropic, yfinance, pandas; print('✅ Dependências instaladas com sucesso!')"
```

### 3️⃣ Configurar Frontend

```bash
# No diretório frontend/
cd frontend
npm install
```

### 4️⃣ Executar o Projeto

#### Backend (API)

**⚠️ IMPORTANTE:** Sempre execute os comandos a partir da **raiz do projeto** (`mini-projeto-equipe08/`), não de dentro do diretório `backend/`. Os imports do projeto usam o prefixo `backend.` e dependem disso.

```bash
# Na raiz do projeto: mini-projeto-equipe08/

# Ativar ambiente virtual
source backend/venv/bin/activate  # macOS/Linux
# backend\venv\Scripts\activate   # Windows

# Executar a API
uvicorn backend.api.main:app --reload
```

Você saberá que o ambiente virtual está ativo quando ver `(venv)` no início da linha do terminal:
```bash
(venv) user@machine mini-projeto-equipe08 %
```

A API estará disponível em `http://localhost:8000`

**Para desativar o ambiente virtual:**
```bash
deactivate
```

**Troubleshooting:**
- **Erro `command not found: uvicorn`** → Você não ativou o ambiente virtual. Execute `source backend/venv/bin/activate` primeiro.
- **Erro `No module named 'backend'`** → Você está rodando de dentro do diretório `backend/`. Volte para a raiz do projeto e use `uvicorn backend.api.main:app --reload`.
- **Erro `No module named 'fastapi'`** → Instale as dependências: `pip install -r backend/requirements.txt`
- **Erro `ANTHROPIC_API_KEY not found`** → Verifique se o arquivo `.env` existe na raiz do projeto com a chave preenchida.

#### Frontend

```bash
# No diretório frontend/
npm run dev
```

O frontend estará disponível em `http://localhost:5173`

#### Testes do Frontend

```bash
# No diretório frontend/
npm test
```

### 🔍 Estrutura de Dependências

#### Backend

| Dependência | Versão | Finalidade |
|---|---|---|
| `fastapi` | 0.115.12 | Framework da API REST |
| `uvicorn` | 0.34.2 | Servidor ASGI |
| `sqlalchemy` | 2.0.40 | ORM para banco de dados |
| `yfinance` | 0.2.61 | Cotações, histórico, DRE e dados de FIIs |
| `fundamentus` | 0.3.2 | Indicadores fundamentalistas de ações da B3 |
| `anthropic` | 0.52.0 | Geração de análises via LLM |
| `pandas` | ≥2.2.0 | Processamento de dados |
| `requests` | ≥2.28.0 | Cliente HTTP (BCB API) |
| `apscheduler` | 3.10.4 | Agendamento do ETL |
| `python-dotenv` | 1.0.1 | Gerenciamento de variáveis de ambiente |
| `pytz` | 2025.2 | Timezone de Brasília (prompt logging) |

#### Frontend

| Dependência | Versão | Finalidade |
|---|---|---|
| `react` | ^19.2.5 | Framework principal |
| `react-dom` | ^19.2.5 | Renderização no DOM |
| `recharts` | ^3.8.1 | Gráficos e visualizações |
| `axios` | ^1.16.0 | Cliente HTTP para chamadas à API |
| `lucide-react` | ^1.14.0 | Ícones |
| `vite` | ^8.0.10 | Build tool e dev server |
| `vitest` | ^4.1.5 | Framework de testes |

### ⚠️ Troubleshooting

**Erro `command not found: uvicorn`:**
- **Causa:** Ambiente virtual não está ativado
- **Solução:** Execute `source backend/venv/bin/activate` (macOS/Linux) ou `backend\venv\Scripts\activate` (Windows) antes de rodar o uvicorn

**Erro ao instalar `yfinance`:**
```bash
pip install --upgrade pip
pip install yfinance --no-cache-dir
```

**Erro ao instalar `pandas` ou `numpy`:**
```bash
# Instalar dependências de sistema (macOS)
brew install openblas

# Instalar dependências de sistema (Ubuntu/Debian)
sudo apt-get install python3-dev libopenblas-dev
```

**Erro "ANTHROPIC_API_KEY not found":**
- Verificar se o arquivo `.env` existe na **raiz do projeto** (não dentro de `backend/`)
- Verificar se a variável está preenchida corretamente
- Reiniciar o servidor após alterar o `.env`

**Ambiente virtual não existe:**
```bash
# Da raiz do projeto
python -m venv backend/venv
source backend/venv/bin/activate  # macOS/Linux
pip install -r backend/requirements.txt
```

---

## 📝 Prompt Logging

Este projeto implementa um sistema automático de **logging de prompts** executados no Kiro, organizado por branch Git. O objetivo é manter rastreabilidade completa das interações com o agente durante o desenvolvimento.

### Como Funciona

Sempre que você submete um prompt ao Kiro, o sistema automaticamente:

- Registra o conteúdo do prompt
- Captura metadados (branch, responsável, data/hora)
- Salva em arquivo Markdown específico da branch
- Mantém histórico incremental e versionável

### Estrutura de Logs

```
.kiro/prompt-logs/
├── main.md                 # Logs da branch main
├── develop.md              # Logs da branch develop
├── feature-auth.md         # Logs de feature/auth
└── bugfix-crash-fix.md     # Logs de bugfix/crash-fix
```

### Consulta de Logs

**Ver logs de uma branch:**
```bash
cat .kiro/prompt-logs/<branch-name>.md
```

**Últimas entradas:**
```bash
tail -n 50 .kiro/prompt-logs/<branch-name>.md
```

**Buscar por palavra-chave:**
```bash
grep -A 10 "palavra-chave" .kiro/prompt-logs/<branch-name>.md
```

### Versionamento de Logs

**Decisão:** Os arquivos de log de prompts **são versionados no Git** por padrão.

**Justificativa:**
- **Rastreabilidade:** Facilita code reviews ao permitir que revisores entendam o contexto das decisões tomadas durante o desenvolvimento
- **Documentação:** Preserva o histórico completo do processo de desenvolvimento para referência futura
- **Compartilhamento de conhecimento:** Permite que membros da equipe aprendam com as interações anteriores
- **Auditoria:** Mantém registro completo das interações com o agente Kiro

**Considerações:**
- Os logs contêm apenas informações do projeto (prompts, metadados de Git)
- Não contêm dados sensíveis (tokens, senhas, chaves de API)
- O formato Markdown facilita diffs legíveis no Git
- Arquivos crescem incrementalmente, mas permanecem em formato texto

**Alternativa:** Se em algum momento o projeto decidir não versionar logs, adicione ao `.gitignore`:
```gitignore
# Prompt logs (desabilitar versionamento)
.kiro/prompt-logs/
```

### Documentação Completa

Para mais detalhes sobre o sistema de prompt logging, incluindo arquitetura, limitações e troubleshooting, consulte:

📖 **[docs/prompt-logging.md](docs/prompt-logging.md)**

---

## 🧩 Arquitetura Implementada

### Backend

- Coleta de dados via Python (fundamentus, yfinance, BCB)
- Processamento e cálculo de indicadores por tipo de ativo
- ETL diário agendado (19h Brasília)
- API REST com FastAPI

### Frontend

- Interface em React com Vite
- Páginas: Home (busca), Análise, Ações, FIIs, Aprendizado
- Componentes: ScoreCard, ScoreRing, IndicatorTable, Chart, Verdict, Sidebar, Header
- Gráficos com Recharts
- Chamadas à API via Axios
- Testes com Vitest + Testing Library

---

## 📌 Pontos de Atenção

- Custos de APIs e infraestrutura
- Atualização e consistência dos dados
- Latência vs processamento prévio
- Escalabilidade
- Clareza no disclaimer

---

## 🧑‍💻 Público-Alvo

- Investidores iniciantes
- Pessoas interessadas em análise fundamentalista
- Usuários que buscam autonomia nas decisões

---

## 📝 Exemplo de Prompt

**Entrada:**
```
Ticker: PETR4
Dados financeiros estruturados
Indicadores calculados
Contexto macro
```

**Saída esperada:**
```
✅ Análise clara e objetiva
➕ Pontos positivos e negativos
🏆 Score do ativo
📚 Explicação didática
🔍 Conclusão com nível de confiança
```

---

## 🤝 Como Contribuir

Contribuições são bem-vindas! Para manter a qualidade e consistência do projeto, siga estas diretrizes:

### Reportar Bugs ou Propor Funcionalidades

Use os **templates de issues** disponíveis:

1. Acesse [Issues](https://github.com/IA-para-DEVs-SCTEC-T2/mini-projeto-fundamentAI/issues/new/choose)
2. Escolha o template apropriado:
   - 🚀 **Feature Request** — Para novas funcionalidades
   - 🐛 **Bug Report** — Para reportar bugs
   - 📚 **Documentation** — Para melhorias na documentação
   - 🔧 **Chore/Maintenance** — Para tarefas de manutenção
   - 💬 **General Issue** — Para outros assuntos
3. Preencha todos os campos obrigatórios

### Contribuir com Código

1. **Fork** o repositório
2. Crie uma **branch** seguindo as convenções em `.kiro/steering/gitflow.md`:
   ```bash
   git checkout -b feature/nome-da-funcionalidade
   ```
3. Faça commits seguindo **Conventional Commits**:
   ```bash
   git commit -m "feat(escopo): descrição da mudança"
   ```
4. **Push** para seu fork:
   ```bash
   git push origin feature/nome-da-funcionalidade
   ```
5. Abra uma **Pull Request** usando o template automático
6. Aguarde revisão e aprovação

### Convenções do Projeto

- **Git Flow**: `.kiro/steering/gitflow.md`
- **Estrutura**: `.kiro/steering/structure.md`
- **Stack Técnica**: `.kiro/steering/tech.md`
- **Produto**: `.kiro/steering/product.md`

### Templates

Todos os templates estão documentados em [`.github/README.md`](.github/README.md).

---

## 📋 Backlog e Roadmap

Acompanhe o progresso do projeto no [Project Board](https://github.com/orgs/IA-para-DEVs-SCTEC-T2/projects/8).

---

*Projeto em desenvolvimento. Contribuições e sugestões são bem-vindas.*
