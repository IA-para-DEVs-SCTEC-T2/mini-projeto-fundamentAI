# Produto: Analisador Fundamentalista de Ações e FIIs da B3

## Visão do Produto

Plataforma web que consolida dados financeiros públicos de empresas e fundos imobiliários listados na B3, aplica critérios objetivos de análise fundamentalista e entrega análises estruturadas com viés educativo — reduzindo a barreira de entrada para investidores iniciantes.

> ⚠️ O produto **não fornece recomendações de investimento**. As análises são informativas e baseadas em dados históricos. A decisão final é sempre do usuário.

---

## Problema

Investidores enfrentam:

- Informações dispersas em múltiplas fontes
- Dificuldade em interpretar indicadores financeiros complexos
- Alto custo de consultorias especializadas
- Tempo elevado para análise de empresas e fundos
- Falta de padronização na avaliação de ativos distintos (ações vs FIIs)

---

## Solução

Uma plataforma que:

- Consolida dados financeiros de múltiplas fontes confiáveis
- Aplica critérios objetivos de análise fundamentalista **por tipo de ativo**
- Gera um veredito estruturado sobre o ativo
- Explica os indicadores de forma acessível
- Apresenta dados comparativos com setor/mercado
- Entrega experiência visual com gráficos e scores

---

## Público-Alvo

- Investidores na B3, especialmente iniciantes
- Pessoas interessadas em análise fundamentalista de ações e FIIs
- Usuários que buscam autonomia nas decisões de investimento

---

## Objetivos

- Auxiliar na análise de ações e FIIs da B3
- Reduzir a barreira de entrada para novos investidores
- Fornecer insumos claros para tomada de decisão
- Servir como ferramenta educativa sobre indicadores financeiros

---

## Escopo Inicial (MVP)

**Dentro do escopo:**
- Ações e FIIs ativos listados na B3 (~937 ativos)
- Análise fundamentalista com indicadores específicos por tipo de ativo
- Dados históricos (não tempo real)
- Score fundamentalista unificado (0-100) para ações e FIIs
- Visualização de gráficos e comparação setorial
- Atualização diária (pós-fechamento do mercado)
- Consulta por ticker
- Identificação e bloqueio de tickers inativos

**Fora do escopo (por ora):**
- Recomendação direta de compra/venda
- Dados em tempo real
- Outros mercados (ex: EUA)
- Análise técnica/gráfica
- Machine Learning para scoring avançado
- Vacância física/financeira de FIIs
- Cap Rate de FIIs

---

## Tipos de Ativos Suportados

### Ações (Empresas da B3)

Foco em eficiência operacional, lucratividade e endividamento.

| Indicador | Descrição | Peso no Score |
|---|---|---|
| P/L (Preço/Lucro) | Quanto o mercado paga por R$1 de lucro | 15% |
| ROE | Retorno sobre Patrimônio Líquido | 20% |
| Dívida Líquida / EBITDA | Nível de alavancagem financeira | 15% |
| Margem Líquida | Eficiência na geração de lucro | 15% |
| EV/EBITDA | Valor da empresa sobre geração de caixa | 10% |
| Dividend Yield | Rendimento distribuído / preço | 10% |
| Crescimento Lucro YoY | CAGR do lucro líquido (via yfinance) | 15% |

**Fonte de dados:** fundamentus (principal) + yfinance (histórico DRE)

### FIIs (Fundos de Investimento Imobiliário)

Foco em geração de renda e valor dos ativos.

| Indicador | Descrição | Peso no Score |
|---|---|---|
| P/VP (Preço/Valor Patrimonial) | Desconto ou prêmio sobre o patrimônio | 30% |
| P/L | Preço sobre rendimento | 15% |
| Dividend Yield | Rendimento distribuído / preço da cota | 35% |
| Crescimento Dividendos YoY | CAGR dos dividendos anuais | 20% |

**Fonte de dados:** yfinance (exclusivo — fundamentus não suporta FIIs)

---

## Score Fundamentalista (Output Unificado)

O score é calculado com indicadores específicos por tipo de ativo, mas o **output é idêntico** para ações e FIIs — garantindo consistência no frontend.

| Score | Classificação |
|---|---|
| 75 – 100 | Excelente |
| 50 – 74 | Bom |
| 25 – 49 | Regular |
| 0 – 24 | Fraco |

---

## Gestão de Tickers Inativos

Tickers sem cotação de mercado ou sem dados financeiros disponíveis são classificados como **inativos** e excluídos da análise.

- Consultas a tickers inativos retornam HTTP 404 com mensagem explicativa
- Lista de inativos mantida na tabela `inactive_tickers` do banco
- Relatório CSV gerado periodicamente para revisão interna (`relatorio_inativos.csv`)

**Critérios de inatividade:**
- Preço de mercado zero ou ausente
- Sem nenhum indicador disponível (ROE, P/L, P/VP todos nulos) E sem dados financeiros

---

## Dados Macroeconômicos

Contexto macroeconômico injetado nos prompts de análise:

| Dado | Fonte | Uso |
|---|---|---|
| SELIC | API BCB (SGS série 11) | Contextualiza custo de capital |
| IPCA | API BCB (SGS série 433) | Contextualiza inflação e retorno real |

---

## Saída Esperada por Análise

Para cada ativo consultado, o sistema retorna:

- Veredito sobre o ativo (Positivo / Neutro / Negativo)
- Score fundamentalista (0-100) com classificação qualitativa
- Explicação dos indicadores em linguagem acessível
- Avaliação de risco
- Pontos positivos e negativos
- Sugestão de momento *(não recomendação de compra/venda)*
- Conclusão com nível de confiança

---

## Evoluções Futuras (Fora do MVP)

- Vacância física e financeira para FIIs de tijolo
- Cap Rate para FIIs
- Inclusão de outros mercados (ex: EUA)
- Carteiras personalizadas
- Alertas inteligentes
- Integração com dados em tempo real
- Machine Learning para scoring avançado
