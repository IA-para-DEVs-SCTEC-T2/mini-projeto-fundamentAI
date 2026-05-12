#!/usr/bin/env python3
"""
Script para criar as issues restantes (3-29) do FundamentAI
"""

import subprocess
import sys

REPO = "IA-para-DEVs-SCTEC-T2/mini-projeto-equipe08"

def create_issue(num, title, labels, body):
    """Cria uma issue no GitHub"""
    cmd = ["gh", "issue", "create", "--repo", REPO, "--title", title, "--body", body]
    for label in labels:
        cmd.extend(["--label", label])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return {"success": True, "url": result.stdout.strip()}
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": e.stderr}

# Definição das issues 3-29
issues = [
    # Issue 3
    {
        "num": 3,
        "title": "feat(collectors): implementar coletor yfinance para ações",
        "labels": ["backend", "collectors", "data"],
        "body": """## Contexto
Implementar coletor de dados financeiros de ações da B3 usando a biblioteca yfinance. Este coletor é responsável por obter cotações, histórico de preços e demonstrativos financeiros.

## Escopo
- Criar `backend/collectors/yfinance.py`
- Implementar função para coletar cotação atual de uma ação
- Implementar função para coletar histórico de preços (últimos 5 anos)
- Implementar função para coletar demonstrativos financeiros (DRE, Balanço Patrimonial)
- Tratar erros de API e tickers inválidos
- Normalizar dados para formato padrão do sistema

## Critérios de Aceite
- [ ] Função `get_stock_quote(ticker)` retorna cotação atual
- [ ] Função `get_price_history(ticker, years=5)` retorna histórico
- [ ] Função `get_financial_statements(ticker)` retorna DRE e Balanço
- [ ] Tratamento de erros para tickers inválidos ou indisponíveis
- [ ] Dados normalizados em formato pandas DataFrame
- [ ] Documentação das funções com exemplos de uso

## Dependências
- #1
- #2

## Referências
- `.kiro/steering/tech.md` (seção Fontes de Dados Externas)
- `.kiro/steering/structure.md` (seção backend/collectors/)"""
    },
    # Issue 4
    {
        "num": 4,
        "title": "feat(collectors): implementar coletor fundamentus para ações",
        "labels": ["backend", "collectors", "data"],
        "body": """## Contexto
Implementar coletor de indicadores fundamentalistas de ações da B3 usando a biblioteca fundamentus. Este coletor complementa os dados do yfinance com indicadores específicos do mercado brasileiro.

## Escopo
- Criar `backend/collectors/fundamentus.py`
- Implementar função para coletar indicadores fundamentalistas (ROE, ROIC, P/L, P/VP, Margem Líquida, Dívida Líquida/EBITDA)
- Implementar função para identificar setor da empresa
- Tratar erros de API e tickers inválidos
- Normalizar dados para formato padrão do sistema

## Critérios de Aceite
- [ ] Função `get_fundamentals(ticker)` retorna todos os indicadores
- [ ] Função `get_sector(ticker)` retorna setor da empresa
- [ ] Tratamento de erros para tickers inválidos ou dados indisponíveis
- [ ] Dados normalizados em formato pandas DataFrame
- [ ] Documentação das funções com exemplos de uso
- [ ] Validação de que os dados são específicos de ações da B3

## Dependências
- #1
- #2

## Referências
- `.kiro/steering/tech.md` (seção Fontes de Dados Externas)
- `.kiro/steering/product.md` (seção Indicadores Fundamentalistas)"""
    },
    # Issue 5
    {
        "num": 5,
        "title": "feat(collectors): implementar coletor API Banco Central",
        "labels": ["backend", "collectors", "data"],
        "body": """## Contexto
Implementar coletor de dados macroeconômicos (SELIC e IPCA) via API do Banco Central. Estes dados são essenciais para contextualizar a análise fundamentalista.

## Escopo
- Criar `backend/collectors/bacen.py`
- Implementar função para coletar taxa SELIC atual e histórica
- Implementar função para coletar IPCA atual e histórico
- Implementar cache para evitar chamadas desnecessárias (dados macro mudam com menor frequência)
- Tratar erros de API e timeouts
- Normalizar dados para formato padrão do sistema

## Critérios de Aceite
- [ ] Função `get_selic()` retorna taxa SELIC atual
- [ ] Função `get_ipca()` retorna IPCA atual
- [ ] Funções com parâmetro opcional para histórico (últimos 12 meses)
- [ ] Cache implementado para reduzir chamadas à API
- [ ] Tratamento de erros e timeouts
- [ ] Documentação das funções com exemplos de uso

## Dependências
- #1
- #2

## Referências
- `.kiro/steering/tech.md` (seção Fontes de Dados Externas)
- `.kiro/steering/product.md` (seção Dados Macroeconômicos)"""
    },
]

print("🚀 Criando issues restantes (3-5) no GitHub...")
print()

results = []
for issue in issues:
    print(f"[{issue['num']}/29] {issue['title']}")
    result = create_issue(issue['num'], issue['title'], issue['labels'], issue['body'])
    if result["success"]:
        print(f"  ✅ {result['url']}")
        results.append({"num": issue['num'], "success": True, "url": result['url']})
    else:
        print(f"  ❌ Erro: {result['error']}")
        results.append({"num": issue['num'], "success": False})

print()
success_count = sum(1 for r in results if r["success"])
print(f"✅ {success_count}/{len(issues)} issues criadas com sucesso")

if success_count < len(issues):
    sys.exit(1)
