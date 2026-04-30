# Produto: Analisador Fundamentalista de Ações da B3

## Visão do Produto

Plataforma web que consolida dados financeiros públicos de empresas listadas na B3, aplica critérios objetivos de análise fundamentalista e entrega análises estruturadas com viés educativo — reduzindo a barreira de entrada para investidores iniciantes.

> ⚠️ O produto **não fornece recomendações de investimento**. As análises são informativas e baseadas em dados históricos. A decisão final é sempre do usuário.

---

## Problema

Investidores enfrentam:

- Informações dispersas em múltiplas fontes
- Dificuldade em interpretar indicadores financeiros complexos
- Alto custo de consultorias especializadas
- Tempo elevado para análise de empresas
- Falta de padronização na avaliação de ativos

---

## Solução

Uma plataforma que:

- Consolida dados financeiros de múltiplas fontes confiáveis
- Aplica critérios objetivos de análise fundamentalista
- Gera um veredito estruturado sobre o ativo
- Explica os indicadores de forma acessível
- Apresenta dados comparativos com setor/mercado
- Entrega experiência visual com gráficos e scores

---

## Público-Alvo

- Investidores na B3, especialmente iniciantes
- Pessoas interessadas em análise fundamentalista
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
- Ações e FIIs listados na B3
- Análise fundamentalista (não análise técnica/gráfica)
- Dados históricos (não tempo real)
- Score fundamentalista por ativo
- Visualização de gráficos e comparação setorial
- Explicação simplificada de DRE e balanços
- Atualização diária (pós-fechamento do mercado)
- Consulta por ticker

**Fora do escopo (por ora):**
- Recomendação direta de compra/venda
- Dados em tempo real
- Outros mercados (ex: EUA)
- Análise técnica/gráfica
- Machine Learning para scoring avançado

---

## Critérios de Análise

### Crescimento Sustentável
- Crescimento anual de receita e lucro líquido ≥ 10%
- Consistência nos últimos 5 anos
- Comparação com empresas do mesmo setor

### Indicadores Fundamentalistas

| Indicador | Descrição |
|---|---|
| ROE | Retorno sobre Patrimônio |
| ROIC | Retorno sobre Capital Investido |
| Margem líquida | Eficiência na geração de lucro |
| Dívida líquida / EBITDA | Nível de alavancagem |
| P/L | Preço / Lucro |
| P/VP | Preço / Valor Patrimonial |

### Dados Macroeconômicos
- SELIC
- IPCA

### Análises Complementares
- Estrutura de capital
- Eficiência operacional
- Comparação setorial
- Tendências históricas

> Notícias podem ser consideradas, mas com peso reduzido.

---

## Saída Esperada por Análise

Para cada ativo consultado, o sistema deve retornar:

- Veredito sobre o ativo
- Explicação dos indicadores
- Avaliação de risco
- Score fundamentalista
- Sugestão de momento *(não recomendação de compra/venda)*
- Pontos positivos e negativos
- Conclusão com nível de confiança

---

## Evoluções Futuras (Fora do MVP)

- Inclusão de outros mercados (ex: EUA)
- Carteiras personalizadas
- Alertas inteligentes
- Integração com dados em tempo real
- Machine Learning para scoring avançado
