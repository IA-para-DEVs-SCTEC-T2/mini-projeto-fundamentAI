# FundamentAI — Wireframes e Mockups Refinados (Telas2)

> Segunda iteração de design do FundamentAI. Contém wireframes de estrutura e mockups refinados gerados a partir do script de prompts definido em `TELA1.md`.

---

## Contexto

Após a primeira rodada de mockups (`docs/Telas1/`), esta iteração aprofunda o design com:

- **Wireframes** — estrutura e layout de cada tela sem estilização final
- **Mockups refinados** — versões com identidade visual aplicada (dark premium, teal `#00e6d2`, roxo `#8a2be2`)
- **Visão consolidada** — todas as telas em uma única imagem para referência rápida

---

## Wireframes

Estrutura base das telas, definindo hierarquia de informação e posicionamento dos componentes.

### Wireframe 1 — Home / Landing Page

![Wireframe 1 — Home](docs/Telas2/wireframe1.png)

---

### Wireframe 2 — Dashboard de Análise

![Wireframe 2 — Dashboard](docs/Telas2/wireframe2.png)

---

### Wireframe 3 — Tela de Loading

![Wireframe 3 — Loading](docs/Telas2/wireframe3.png)

---

### Wireframe 4 — Tela de Erro / Aviso

![Wireframe 4 — Erro](docs/Telas2/wireframe4.png)

---

### Wireframe 5 — Indicadores por Tipo de Ativo

![Wireframe 5 — Indicadores](docs/Telas2/wireframe5.png)

---

## Mockups Refinados

Versões com identidade visual completa aplicada sobre os wireframes.

### Mock 6

![Mock 6](docs/Telas2/mock6.png)

---

### Mock 7

![Mock 7](docs/Telas2/mock7.png)

---

### Mock 8

![Mock 8](docs/Telas2/mock8.png)

---

### Mock 9

![Mock 9](docs/Telas2/mock9.png)

---

## Visão Consolidada — Todas as Telas

Panorama completo do produto com todas as telas e fluxo de navegação.

![Todas as Telas](docs/Telas2/todasTelas.png)

---

## Referências

- Primeira iteração de mockups: [`TELA1.md`](TELA1.md)
- Mapeamento completo de imagens: [`docs/mockupPreviews.md`](docs/mockupPreviews.md)
- Paleta de cores e identidade visual: ver seção "Paleta de Cores" em `TELA1.md`
- Componentes implementados: `frontend/src/components/` e `frontend/src/pages/`

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
Pontuação de 0 a 100, independente do tipo de ativo, classificando em quatro categorias:

| Score | Classificação |
|---|---|
| 75 – 100 | Excelente |
| 50 – 74 | Bom |
| 25 – 49 | Regular |
| 0 – 24 | Fraco |

**Análises Explicativas com Inteligência Artificial**
Utilizando a API da Anthropic (modelos Claude), o sistema interpreta os indicadores financeiros e o cenário macroeconômico para gerar:
- Veredito estruturado
- Avaliação de risco
- Explicações didáticas dos indicadores

> ⚠️ O objetivo é estritamente educativo — sem recomendações diretas de investimento.

**Garantia de Qualidade de Dados (ETL)**
Scripts automáticos exigem no mínimo 3 indicadores disponíveis por ativo. Se faltarem dados em uma fonte, o sistema tenta calcular derivados ou busca em fontes alternativas.

**Gestão de Ativos Inativos**
Tickers sem dados suficientes são identificados, bloqueados de análises e sinalizados com mensagem explicativa ao usuário.

**Visualização e Comparação**
Frontend com gráficos de histórico de preços e comparação setorial.

**Atualizações Diárias**
Banco de dados e análises atualizados diariamente após o fechamento do mercado (19h, horário de Brasília).

---

## Script de Prompts para Design

> Os prompts abaixo estão em inglês — padrão que gera melhores resultados em ferramentas de IA geradora de imagens (Midjourney, DALL-E 3, Figma AI). As interfaces devem ser criadas em **Português do Brasil**.

---

## 📏 Prompts para Wireframes (Estrutura de Layout)

Foco em estrutura e hierarquia, tons de cinza, estilo sketch.

---

### Wireframe — Tela 1: Dashboard Inicial (Home / Busca)

**Objetivo:** Tela inicial limpa onde o usuário busca o ativo e visualiza opções recentes, reduzindo a barreira de entrada.

```
UI/UX wireframe of a financial web application dashboard, landing page for stock analysis,
prominent large search bar in the center for stock tickers, educational banners below,
list of recently analyzed assets in small cards, grayscale, minimalist, sketch style,
clean layout, placeholder text, web design --ar 16:9
```

---

### Wireframe — Tela 2: Visão de Ações (Stocks) — Indicadores e Gráfico

**Objetivo:** Tela para ações da B3 com score fundamentalista e grade de indicadores de eficiência (P/L, ROE, Margem Líquida).

```
UI/UX wireframe of a stock asset details screen, top header with ticker name and a large
circular score gauge from 0 to 100, grid of fundamental indicators below like P/E and ROE,
line chart for historical prices at the bottom, web design, grayscale, clean grid structure,
clear hierarchy --ar 16:9
```

---

### Wireframe — Tela 3: Visão de Fundos Imobiliários (FIIs)

**Objetivo:** Adaptação da tela para FIIs, priorizando Score unificado, Dividend Yield e P/VP.

```
UI/UX wireframe of a Real Estate Fund details screen for a financial app, top header with
ticker name and overall score, prominent indicator boxes for Dividend Yield and P/VP,
bar chart for historical dividends distribution, web design layout, grayscale,
structured and organized --ar 16:9
```

---

### Wireframe — Tela 4: Painel de Análise da Inteligência Artificial

**Objetivo:** Espaço dedicado ao veredito do modelo Claude (Anthropic), explicações educativas e dados macroeconômicos (SELIC, IPCA).

```
UI/UX wireframe of an AI analysis panel in a financial web app, large text blocks for AI
verdict, risk assessment section, educational tooltips next to terms, macro economic data
section showing interest rates, clean web layout, grayscale, structured text hierarchy
--ar 16:9
```

---

### Wireframe — Tela 5: Ativo Inativo / Sem Dados (Error State)

**Objetivo:** Interface amigável para quando o sistema bloqueia tickers inativos ou sem os 3 indicadores mínimos exigidos.

```
UI/UX wireframe of an empty state or error screen for a financial app, soft warning
illustration in the center, message box explaining "Ticker Inactive or Insufficient Data",
clean minimalist design, single "Go Back to Home" button, grayscale, simple web design
--ar 16:9
```

---

## 🎨 Prompts para Mockups (Alta Fidelidade)

Foco em UI/UX, cores, tipografia e identidade visual final.

---

### Mockup — Tela 6: Dashboard Inicial (Home)

**Objetivo:** Interface moderna e que transmita confiança, baseada em React.

```
High fidelity UI/UX mockup of a modern financial web application, "FundamentAI" dashboard,
modern clean aesthetic, trust-inspiring blue and green color palette, large central search
bar, recent asset cards with micro-charts, react components style, dribbble trending,
highly detailed, light mode --ar 16:9
```

---

### Mockup — Tela 7: Score Fundamentalista

**Objetivo:** Visualização de alta fidelidade do Score unificado (0–100) mostrando classificação "Excelente" (75–100).

```
High fidelity UI/UX mockup of a stock analysis screen, featuring a prominent color-coded
circular gauge showing a score of 85 "Excellent" in green, ticker name PETR4, modern
dashboard widgets, clean typography, financial app, light theme, soft drop shadows,
dribbble style web design --ar 16:9
```

---

### Mockup — Tela 8: Grade de Indicadores (Ações / FIIs)

**Objetivo:** Cards de dados (P/L, ROE, DY) com foco na experiência visual educativa.

```
High fidelity UI/UX mockup of a financial indicators grid, cards showing P/E ratio, ROE,
and Dividend Yield, elegant hover tooltips for educational purposes explaining the metrics,
modern data visualization, clean white background with subtle shadows, premium UI design,
web application --ar 16:9
```

---

### Mockup — Tela 9: Veredito da IA e Disclaimer

**Objetivo:** Tela elegante com a explicação gerada pela LLM e o disclaimer obrigatório de que não é recomendação de investimento.

```
High fidelity UI/UX mockup of an AI financial analysis report screen, modern interface,
glowing subtle AI sparkle icon, well-formatted text blocks for verdict and risk evaluation,
prominent red disclaimer badge "Not investment advice", sleek modern web design,
clear typography, light mode --ar 16:9
```

---

### Mockup — Tela 10: Comparação Setorial

**Objetivo:** Tela visual para comparar ativos do mesmo setor lado a lado, com diferenças nos indicadores destacadas.

```
High fidelity UI/UX mockup of a financial comparison tool, clean side-by-side data table
comparing three stock tickers, highlighting the fundamentalist score row with color tags,
indicator rows with clean numbers, modern UI structure, trust-inspiring colors,
web application, highly detailed --ar 16:9
```

---

> **Nota:** Todos os prompts acima podem ser usados diretamente em ferramentas como **Midjourney**, **DALL-E 3**, **Figma AI** ou **Galileo AI** para geração das telas. As interfaces resultantes devem estar em **Português do Brasil**.
