# 📊 Analisador Fundamentalista de Ações da B3

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

### 📈 Crescimento Sustentável

- Crescimento anual de receita e lucro líquido ≥ 10%
- Consistência nos últimos 5 anos
- Comparação com empresas do mesmo setor

### 💰 Indicadores Fundamentalistas

| Indicador | Descrição |
|---|---|
| ROE | Retorno sobre Patrimônio |
| ROIC | Retorno sobre Capital Investido |
| Margem líquida | Eficiência na geração de lucro |
| Dívida líquida / EBITDA | Nível de alavancagem |
| P/L | Preço / Lucro |
| P/VP | Preço / Valor Patrimonial |

### 🏦 Dados Macroeconômicos

- SELIC
- IPCA

### 📊 Análises Complementares

- Estrutura de capital
- Eficiência operacional
- Comparação setorial
- Tendências históricas

> Notícias podem ser consideradas, mas com peso reduzido.

---

## ⚙️ Arquitetura

### 🔧 Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python |
| Frontend | React |
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

- `yfinance`
- `fundamentus`
- API do Banco Central (SELIC, IPCA)
- *(Possível expansão: API oficial da B3)*

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

## 🖥️ Funcionalidades

- Consulta por ticker (ações e FIIs)
- Score fundamentalista
- Visualização de gráficos
- Comparação com setor
- Explicação simplificada de DRE e balanços
- Atualização diária (pós-fechamento do mercado)

---

## 🔐 Segurança e Privacidade

- Dados utilizados são públicos
- Avaliar necessidade de cadastro de carteira do usuário
  - Caso implementado:
    - Armazenamento seguro (criptografia)
    - Boas práticas de autenticação

---

## 📦 Escopo Inicial

- Foco em ações da B3
- Análise fundamentalista (não técnico)
- Dados históricos (não tempo real)
- Sem recomendação direta de compra/venda

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

## 🧩 Como Implementar

### Backend

- Scripts Python para coleta e processamento
- ETL diário
- API para servir dados processados

### Frontend

- Interface em React
- Dashboard com gráficos
- Visualização de análises

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

*Projeto em desenvolvimento. Contribuições e sugestões são bem-vindas.*
