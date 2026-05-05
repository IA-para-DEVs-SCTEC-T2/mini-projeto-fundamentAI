#!/bin/bash

# Script para criar issues no GitHub e adicionar ao Project 8
# Repositório: IA-para-DEVs-SCTEC-T2/mini-projeto-equipe08
# Project: https://github.com/orgs/IA-para-DEVs-SCTEC-T2/projects/8

REPO="IA-para-DEVs-SCTEC-T2/mini-projeto-equipe08"
PROJECT_NUMBER=8

echo "🚀 Iniciando criação de issues..."
echo ""

# Issue 1
echo "📝 Criando issue #1..."
gh issue create \
  --repo "$REPO" \
  --title "setup: configurar estrutura inicial do projeto" \
  --label "setup,backend,frontend" \
  --body "## Contexto
Criar a estrutura base do projeto FundamentAI conforme definido em \`.kiro/steering/structure.md\`. Esta é a fundação sobre a qual todo o sistema será construído.

## Escopo
- Criar estrutura de diretórios do backend (collectors/, processors/, etl/, prompts/, api/, db/, tests/)
- Criar estrutura de diretórios do frontend (src/components/, src/pages/, src/services/, src/hooks/, src/utils/)
- Configurar ambiente Python com \`requirements.txt\` inicial
- Configurar ambiente React com \`package.json\` e dependências base
- Configurar \`.gitignore\` adequado para Python e React
- Criar arquivos README.md em diretórios principais

## Critérios de Aceite
- [ ] Estrutura de diretórios do backend criada conforme \`structure.md\`
- [ ] Estrutura de diretórios do frontend criada conforme \`structure.md\`
- [ ] \`requirements.txt\` com dependências base (FastAPI, SQLAlchemy, pandas, yfinance, anthropic)
- [ ] \`package.json\` com dependências base (React, React Router, Axios)
- [ ] \`.gitignore\` configurado para não versionar \`node_modules/\`, \`__pycache__/\`, \`.env\`, etc.
- [ ] Projeto pode ser inicializado localmente (backend e frontend)

## Dependências
- nenhuma

## Referências
- \`.kiro/steering/structure.md\`
- \`.kiro/steering/tech.md\`"

echo ""

# Issue 2
echo "📝 Criando issue #2..."
gh issue create \
  --repo "$REPO" \
  --title "setup: configurar banco de dados e ORM" \
  --label "setup,backend,database" \
  --body "## Contexto
Configurar a camada de persistência de dados usando SQLAlchemy como ORM, com suporte para SQLite (desenvolvimento) e PostgreSQL (produção).

## Escopo
- Criar modelos de dados em \`backend/db/models.py\` para armazenar dados financeiros, indicadores e análises
- Implementar repository pattern em \`backend/db/repository.py\` para abstração de acesso aos dados
- Configurar conexão com banco de dados (SQLite local por padrão)
- Criar migrations iniciais
- Implementar funções CRUD básicas

## Critérios de Aceite
- [ ] Modelos SQLAlchemy criados para: Ticker, FinancialData, Indicators, Analysis
- [ ] Repository implementado com métodos CRUD
- [ ] Conexão com SQLite funcional
- [ ] Código preparado para migração futura para PostgreSQL (uso de variáveis de ambiente)
- [ ] Migrations funcionando corretamente
- [ ] Testes básicos de persistência passando

## Dependências
- #1

## Referências
- \`.kiro/steering/tech.md\` (seção Backend - SQLAlchemy)
- \`.kiro/steering/structure.md\` (seção backend/db/)"

echo ""

# Issue 3
echo "📝 Criando issue #3..."
gh issue create \
  --repo "$REPO" \
  --title "feat(collectors): implementar coletor yfinance para ações" \
  --label "backend,collectors,data" \
  --body "## Contexto
Implementar coletor de dados financeiros de ações da B3 usando a biblioteca yfinance. Este coletor é responsável por obter cotações, histórico de preços e demonstrativos financeiros.

## Escopo
- Criar \`backend/collectors/yfinance.py\`
- Implementar função para coletar cotação atual de uma ação
- Implementar função para coletar histórico de preços (últimos 5 anos)
- Implementar função para coletar demonstrativos financeiros (DRE, Balanço Patrimonial)
- Tratar erros de API e tickers inválidos
- Normalizar dados para formato padrão do sistema

## Critérios de Aceite
- [ ] Função \`get_stock_quote(ticker)\` retorna cotação atual
- [ ] Função \`get_price_history(ticker, years=5)\` retorna histórico
- [ ] Função \`get_financial_statements(ticker)\` retorna DRE e Balanço
- [ ] Tratamento de erros para tickers inválidos ou indisponíveis
- [ ] Dados normalizados em formato pandas DataFrame
- [ ] Documentação das funções com exemplos de uso

## Dependências
- #1
- #2

## Referências
- \`.kiro/steering/tech.md\` (seção Fontes de Dados Externas)
- \`.kiro/steering/structure.md\` (seção backend/collectors/)"

echo ""

# Issue 4
echo "📝 Criando issue #4..."
gh issue create \
  --repo "$REPO" \
  --title "feat(collectors): implementar coletor fundamentus para ações" \
  --label "backend,collectors,data" \
  --body "## Contexto
Implementar coletor de indicadores fundamentalistas de ações da B3 usando a biblioteca fundamentus. Este coletor complementa os dados do yfinance com indicadores específicos do mercado brasileiro.

## Escopo
- Criar \`backend/collectors/fundamentus.py\`
- Implementar função para coletar indicadores fundamentalistas (ROE, ROIC, P/L, P/VP, Margem Líquida, Dívida Líquida/EBITDA)
- Implementar função para identificar setor da empresa
- Tratar erros de API e tickers inválidos
- Normalizar dados para formato padrão do sistema

## Critérios de Aceite
- [ ] Função \`get_fundamentals(ticker)\` retorna todos os indicadores
- [ ] Função \`get_sector(ticker)\` retorna setor da empresa
- [ ] Tratamento de erros para tickers inválidos ou dados indisponíveis
- [ ] Dados normalizados em formato pandas DataFrame
- [ ] Documentação das funções com exemplos de uso
- [ ] Validação de que os dados são específicos de ações da B3

## Dependências
- #1
- #2

## Referências
- \`.kiro/steering/tech.md\` (seção Fontes de Dados Externas)
- \`.kiro/steering/product.md\` (seção Indicadores Fundamentalistas)"

echo ""

# Issue 5
echo "📝 Criando issue #5..."
gh issue create \
  --repo "$REPO" \
  --title "feat(collectors): implementar coletor API Banco Central" \
  --label "backend,collectors,data" \
  --body "## Contexto
Implementar coletor de dados macroeconômicos (SELIC e IPCA) via API do Banco Central. Estes dados são essenciais para contextualizar a análise fundamentalista.

## Escopo
- Criar \`backend/collectors/bacen.py\`
- Implementar função para coletar taxa SELIC atual e histórica
- Implementar função para coletar IPCA atual e histórico
- Implementar cache para evitar chamadas desnecessárias (dados macro mudam com menor frequência)
- Tratar erros de API e timeouts
- Normalizar dados para formato padrão do sistema

## Critérios de Aceite
- [ ] Função \`get_selic()\` retorna taxa SELIC atual
- [ ] Função \`get_ipca()\` retorna IPCA atual
- [ ] Funções com parâmetro opcional para histórico (últimos 12 meses)
- [ ] Cache implementado para reduzir chamadas à API
- [ ] Tratamento de erros e timeouts
- [ ] Documentação das funções com exemplos de uso

## Dependências
- #1
- #2

## Referências
- \`.kiro/steering/tech.md\` (seção Fontes de Dados Externas)
- \`.kiro/steering/product.md\` (seção Dados Macroeconômicos)"

echo ""

echo "✅ Issues 1-5 criadas com sucesso!"
echo "Pressione Enter para continuar com as próximas issues..."
read

