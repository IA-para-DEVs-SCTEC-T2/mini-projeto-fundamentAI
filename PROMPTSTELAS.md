# FundamentAI — Prompts de Telas e Roadmap Visual de Navegação

> Prompts prontos para geração de wireframes e mockups em ferramentas de IA (Midjourney, DALL-E 3, Figma AI), mais o roadmap de navegação para prototipação no Figma.

---

## Sobre o FundamentAI

O **FundamentAI** é uma plataforma focada em ajudar investidores iniciantes a analisar empresas e fundos listados na B3 (ações e FIIs) de forma fundamentada em dados e Inteligência Artificial.

### Principais Funcionalidades

**Consolidação de Dados Financeiros**
A plataforma agrega dados públicos de múltiplas fontes: Fundamentus (ações), yfinance (histórico e FIIs) e API do Banco Central (contexto macroeconômico: SELIC e IPCA).

**Cálculo de Indicadores Específicos por Tipo de Ativo**
- **Ações:** indicadores operacionais e de lucratividade — P/L, ROE, Margem Líquida
- **FIIs:** foco em geração de renda e valor — P/VP e Dividend Yield

**Score Fundamentalista Unificado**
Pontuação de 0 a 100, independente do tipo de ativo:

| Score | Classificação |
|---|---|
| 75 – 100 | Excelente |
| 50 – 74 | Bom |
| 25 – 49 | Regular |
| 0 – 24 | Fraco |

**Análises Explicativas com Inteligência Artificial**
Utilizando a API da Anthropic (modelos Claude), o sistema gera veredito estruturado, avaliações de risco e explicações didáticas dos indicadores.

> ⚠️ O objetivo é estritamente educativo — sem recomendações diretas de investimento.

**Garantia de Qualidade de Dados (ETL)**
Scripts automáticos exigem no mínimo 3 indicadores disponíveis por ativo. Se faltarem dados, o sistema tenta calcular derivados ou busca em fontes alternativas.

**Gestão de Ativos Inativos**
Tickers sem dados suficientes são identificados, bloqueados e sinalizados com mensagem explicativa ao usuário.

**Visualização e Comparação**
Frontend com gráficos de histórico de preços e comparação setorial.

**Atualizações Diárias**
Banco de dados atualizado diariamente após o fechamento do mercado (19h, horário de Brasília).

---

## Dica de Uso dos Prompts

> Os prompts estão em **inglês** — padrão que gera melhores resultados em ferramentas de IA geradora de imagens (Midjourney, DALL-E 3, Figma AI). As interfaces resultantes devem ser criadas em **Português do Brasil**.

---

## 📏 Wireframes — Estrutura de Layout (verde, roxo, laranja, amarelo)

---

### Tela 1 — Dashboard Inicial (Home / Busca)

**Objetivo:** Tela inicial limpa onde o usuário busca o ativo e visualiza opções recentes, reduzindo a barreira de entrada.

```
UI/UX wireframe of a financial web application dashboard, landing page for stock analysis,
prominent large search bar in the center for stock tickers, educational banners below,
list of recently analyzed assets in small cards, greenscale, purple, orange, yellow,
clean grid structure, minimalist, sketch style, clean layout, placeholder text,
web design --ar 16:9
```

---

### Tela 2 — Visão de Ações (Stocks) — Indicadores e Gráfico

**Objetivo:** Tela para ações da B3 com score fundamentalista e grade de indicadores de eficiência (P/L, ROE, Margem Líquida).

```
UI/UX wireframe of a stock asset details screen, top header with ticker name and a large
circular score gauge from 0 to 100, grid of fundamental indicators below like P/E and ROE,
line chart for historical prices at the bottom, web design, greenscale, purple, orange,
yellow, clean grid structure, clear hierarchy --ar 16:9
```

---

### Tela 3 — Visão de Fundos Imobiliários (FIIs)

**Objetivo:** Adaptação da tela para FIIs, priorizando Score unificado, Dividend Yield e P/VP.

```
UI/UX wireframe of a Real Estate Fund details screen for a financial app, top header with
ticker name and overall score, prominent indicator boxes for Dividend Yield and P/VP,
bar chart for historical dividends distribution, web design layout, greenscale, purple,
orange, yellow, clean grid structure, structured and organized --ar 16:9
```

---

### Tela 4 — Painel de Análise da Inteligência Artificial

**Objetivo:** Espaço dedicado ao veredito do modelo Claude (Anthropic), explicações educativas e dados macroeconômicos (SELIC, IPCA).

```
UI/UX wireframe of an AI analysis panel in a financial web app, large text blocks for AI
verdict, risk assessment section, educational tooltips next to terms, macro economic data
section showing interest rates, clean web layout, greenscale, purple, orange, yellow,
clean grid structure, structured text hierarchy --ar 16:9
```

---

### Tela 5 — Ativo Inativo / Sem Dados (Error State)

**Objetivo:** Interface amigável para quando o sistema bloqueia tickers inativos ou sem os 3 indicadores mínimos exigidos.

```
UI/UX wireframe of an empty state or error screen for a financial app, soft warning
illustration in the center, message box explaining "Ticker Inactive or Insufficient Data",
clean minimalist design, single "Go Back to Home" button, greenscale, purple, orange,
yellow, clean grid structure, simple web design --ar 16:9
```

---

## 🎨 Mockups — Alta Fidelidade (cores e tipografia)

---

### Tela 6 — Dashboard Inicial (Home)

**Objetivo:** Interface moderna que transmita confiança, baseada em React.

```
High fidelity UI/UX mockup of a modern financial web application, "FundamentAI" dashboard,
modern clean aesthetic, trust-inspiring blue and green color palette, large central search
bar, recent asset cards with micro-charts, react components style, dribbble trending,
highly detailed, light mode --ar 16:9
```

---

### Tela 7 — Score Fundamentalista (Ações / FIIs)

**Objetivo:** Visualização de alta fidelidade do Score unificado (0–100) mostrando classificação "Excelente" (75–100).

```
High fidelity UI/UX mockup of a stock analysis screen, featuring a prominent color-coded
circular gauge showing a score of 85 "Excellent" in green, ticker name PETR4, modern
dashboard widgets, clean typography, financial app, light theme, soft drop shadows,
dribbble style web design --ar 16:9
```

---

### Tela 8 — Grade de Indicadores (P/L, ROE, DY)

**Objetivo:** Cards de dados com foco na experiência visual educativa.

```
High fidelity UI/UX mockup of a financial indicators grid, cards showing P/E ratio, ROE,
and Dividend Yield, elegant hover tooltips for educational purposes explaining the metrics,
modern data visualization, clean white background with subtle shadows, premium UI design,
web application --ar 16:9
```

---

### Tela 9 — Veredito da IA e Disclaimer

**Objetivo:** Tela elegante com a explicação gerada pela LLM e o disclaimer obrigatório de que não é recomendação de investimento.

```
High fidelity UI/UX mockup of an AI financial analysis report screen, modern interface,
glowing subtle AI sparkle icon, well-formatted text blocks for verdict and risk evaluation,
prominent red disclaimer badge "Not investment advice", sleek modern web design,
clear typography, light mode --ar 16:9
```

---

### Tela 10 — Comparação Setorial

**Objetivo:** Tela visual para comparar ativos do mesmo setor lado a lado, com diferenças nos indicadores destacadas.

```
High fidelity UI/UX mockup of a financial comparison tool, clean side-by-side data table
comparing three stock tickers, highlighting the fundamentalist score row with color tags,
indicator rows with clean numbers, modern UI structure, trust-inspiring colors,
web application, highly detailed --ar 16:9
```

---

## 🗺️ Roadmap Visual de Navegação

Fluxo de navegação lógico para o usuário iniciante — base para prototipação no Figma.

---

### 1. Dashboard Inicial (Home)

**Entrada principal do usuário.**

| Elemento | Descrição |
|---|---|
| Barra de busca central | Campo para digitar o ticker |
| Cards de ativos recentes | Acesso rápido a análises anteriores |
| Banners educativos | Dicas e contexto para iniciantes |

**Ações possíveis:**
- Buscar um ativo → leva para **Visão de Ações** ou **Visão de FIIs**
- Explorar ativos recentes → abre diretamente a tela correspondente

---

### 2. Visão de Ações (Stocks)

**Exibida quando o ticker buscado é uma ação.**

| Elemento | Descrição |
|---|---|
| Score fundamentalista | Gauge circular 0–100 |
| Indicadores principais | P/L, ROE, Margem Líquida |
| Gráfico histórico de preços | Evolução nos últimos 5 anos |

**Ações possíveis:**
- Abrir painel de análise da IA → vai para **Painel de Análise da IA**
- Comparar com outros ativos → leva para **Comparação Setorial**

---

### 3. Visão de Fundos Imobiliários (FIIs)

**Exibida quando o ticker buscado é um FII.**

| Elemento | Descrição |
|---|---|
| Score unificado | Gauge circular 0–100 |
| Indicadores principais | Dividend Yield, P/VP |
| Gráfico de dividendos | Distribuição histórica |

**Ações possíveis:**
- Abrir painel de análise da IA → vai para **Painel de Análise da IA**
- Comparar com outros FIIs → leva para **Comparação Setorial**

---

### 4. Painel de Análise da Inteligência Artificial

**Tela educativa com explicações do modelo Claude.**

| Elemento | Descrição |
|---|---|
| Veredito estruturado | Análise gerada pela LLM |
| Avaliação de risco | Nível de risco do ativo |
| Dados macroeconômicos | SELIC e IPCA em contexto |
| Disclaimer visual | "Não é recomendação de investimento" |

**Ações possíveis:**
- Voltar para o ativo analisado
- Ir para **Comparação Setorial**

---

### 5. Tela de Ativo Inativo / Sem Dados

**Estado de erro amigável.**

| Elemento | Descrição |
|---|---|
| Ilustração de aviso | Feedback visual claro |
| Mensagem explicativa | Motivo do bloqueio do ticker |
| Botão "Voltar para Home" | Ação de retorno |

**Ações possíveis:**
- Retornar ao **Dashboard Inicial**

---

### 6. Tela de Comparação Setorial

**Tela de comparação lado a lado.**

| Elemento | Descrição |
|---|---|
| Tabela com múltiplos tickers | Até 3 ativos simultâneos |
| Score fundamentalista destacado | Comparação visual por cor |
| Indicadores comparativos | P/L, ROE, DY, P/VP |

**Ações possíveis:**
- Voltar ao ativo individual
- Buscar novo ativo → retorna ao **Dashboard Inicial**

---

## 🔄 Fluxo Resumido

```
Home
 ├── Busca ativo (Ação)  → Visão de Ações  → Painel IA → Comparação Setorial
 │                                          ↘ Voltar ao ativo
 ├── Busca ativo (FII)   → Visão de FIIs   → Painel IA → Comparação Setorial
 │                                          ↘ Voltar ao ativo
 └── Ticker inativo      → Tela de Erro    → Voltar para Home

Comparação Setorial → Buscar novo ativo → Home
```

---

## Referências

- Primeira iteração de mockups: [`TELA1.md`](TELA1.md)
- Segunda iteração (wireframes + mockups refinados): [`TELA2.md`](TELA2.md)
- Mapeamento de imagens: [`docs/mockupPreviews.md`](docs/mockupPreviews.md)
