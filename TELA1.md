# FundamentAI — Script de Prompt para Design de Telas

> Este documento contém os prompts prontos para uso em ferramentas de design com IA (Figma AI, v0.dev, Lovable, Galileo AI, etc.) para criação das telas do FundamentAI.

---

## Contexto do Produto

**FundamentAI** é uma plataforma web de análise fundamentalista de ações e FIIs da B3, voltada para investidores iniciantes. O sistema coleta dados públicos, calcula indicadores, gera um score (0–100) e produz análises via IA (Claude/Anthropic). O frontend é em **React**, com visual **dark premium** (fundo escuro, acentos em teal `#00e6d2` e roxo `#8a2be2`).

---

## Paleta de Cores e Identidade Visual

```
Background base:   #0f1115
Background painel: #161a22
Primária (teal):   #00e6d2
Secundária (roxo): #8a2be2
Texto principal:   #f0f3f8
Texto secundário:  #8b949e
Sucesso (verde):   #2ea043
Alerta (amarelo):  #d29922
Perigo (vermelho): #f85149
Fonte display:     Outfit (títulos)
Fonte corpo:       Inter (textos)
Estilo:            Dark premium, glassmorphism, bordas sutis rgba(255,255,255,0.08)
```

---

## Telas a Criar

1. **Home / Landing Page** — Apresentação do produto e busca inicial
2. **Dashboard de Análise** — Resultado completo da análise de um ativo
3. **Tela de Loading** — Estado de carregamento durante processamento
4. **Tela de Erro / Ticker Inativo** — Feedback de erro ou ativo não encontrado
5. **Componente: Indicadores por Tipo de Ativo** — Card diferenciado para Ações e FIIs
6. **Versão Mobile** — Adaptação responsiva do dashboard

---

## Previews das Telas Implementadas

### Tela 1 — Home / Landing Page

> Exibe headline, barra de busca com chips de exemplo (PETR4, VALE3, ITUB4, HGLG11) e os 3 cards de features (Dados Consolidados, Score Fundamentalista, Análise por IA).

---

### Tela 2 — Dashboard de Análise

> Dashboard principal com grid 2 colunas: coluna esquerda (hero do ticker, indicadores, score) e coluna direita (diagnóstico da IA, pontos fortes/atenção, histórico de preços).

---

### Tela 3 — Loading

> Tela de carregamento com spinner animado, texto "Processando Inteligência de Mercado..." e etapas de progresso (Coletar → Calcular → IA).

---

### Tela 4 — Aviso / Erro

> Feedback para ticker não encontrado, ativo inativo ou erro de conexão. Card centralizado com ícone, mensagem explicativa e botão de ação.

---

### Tela 5 — Indicadores por Tipo de Ativo

> Componente com dois estados: badge AÇÃO (teal) com 6 indicadores e badge FII (roxo) com 4 indicadores específicos, cada um com tooltip explicativo.

---

### Mockup Geral

> Visão geral do produto com todas as telas e fluxo de navegação.

---

## PROMPT 1 — Home / Landing Page

```
Crie uma landing page dark premium para uma plataforma web chamada FundamentAI.

IDENTIDADE VISUAL:
- Fundo: #0f1115 com gradiente radial sutil em teal (#00e6d2, 3% opacidade) no canto superior esquerdo e roxo (#8a2be2, 3% opacidade) no canto superior direito
- Tipografia: Outfit para títulos, Inter para corpo
- Estilo: dark premium, glassmorphism, bordas rgba(255,255,255,0.08)
- Cor de destaque: #00e6d2 (teal)

HEADER (fixo, sticky):
- Logo à esquerda: ícone de atividade/gráfico em teal + texto "FundamentAI" em gradiente branco→teal, fonte Outfit bold
- Fundo: rgba(15,17,21,0.8) com backdrop-filter blur

HERO SECTION (centralizado, altura ~70vh):
- Headline principal: "Análise Fundamentalista com Inteligência Artificial" — fonte Outfit, 3.5rem, bold, gradiente branco→teal
- Subtítulo: "Consolide dados da B3, calcule indicadores e receba análises estruturadas geradas por IA para tomar decisões mais informadas." — Inter, 1.2rem, cor #8b949e
- Barra de busca centralizada, pill shape (border-radius 30px), largura máx 520px:
  - Ícone de lupa à esquerda em #8b949e
  - Input placeholder: "Digite um Ticker (ex: PETR4, VALE3, HGLG11)"
  - Botão "Analisar" à direita, fundo #00e6d2, texto escuro, border-radius 24px
  - Fundo do input: #161a22, borda rgba(255,255,255,0.08)
  - Focus state: borda #00e6d2, glow rgba(0,230,210,0.15)
- Chips de exemplo abaixo da busca: "PETR4", "VALE3", "ITUB4", "HGLG11" — pequenos, clicáveis, fundo rgba(0,230,210,0.1), borda rgba(0,230,210,0.3), texto teal

SEÇÃO DE FEATURES (3 cards em grid):
- Card 1: ícone de banco de dados + "Dados Consolidados" + "Agrega yfinance, Fundamentus e Banco Central em uma única análise"
- Card 2: ícone de score/troféu + "Score Fundamentalista" + "Pontuação 0–100 com classificação: Excelente, Bom, Regular ou Fraco"
- Card 3: ícone de IA/cérebro + "Análise por IA" + "Claude (Anthropic) gera veredito, pontos fortes, riscos e sugestão de momento"
- Cards: glassmorphism, fundo rgba(255,255,255,0.03), borda rgba(255,255,255,0.08), hover com borda rgba(0,230,210,0.3) e glow sutil

DISCLAIMER (rodapé da página):
- Texto pequeno, centralizado, cor #8b949e:
  "Esta análise é informativa e baseada em dados históricos públicos. Não constitui recomendação de investimento. A decisão final é sempre do usuário."

RESPONSIVIDADE: Mobile-first, breakpoint 768px para grid de features.
```

---

## PROMPT 2 — Dashboard de Análise (tela principal)

```
Crie o dashboard de análise de ativos para o FundamentAI. Esta é a tela principal após o usuário buscar um ticker.

IDENTIDADE VISUAL: dark premium, fundo #0f1115, acentos teal #00e6d2 e roxo #8a2be2, glassmorphism.

HEADER (igual à Home):
- Logo "FundamentAI" à esquerda
- Barra de busca compacta ao centro (largura máx 400px), com o ticker atual preenchido
- Botão "Analisar" em teal

LAYOUT PRINCIPAL (grid 2 colunas em desktop: 350px | 1fr):

=== COLUNA ESQUERDA ===

CARD HERO DO TICKER:
- Ticker em destaque: "PETR4" — Outfit, 3rem, bold, gradiente branco→cinza
- Subtítulo: "Petróleo Brasileiro S.A. • Petróleo, Gás e Biocombustíveis" — uppercase, letter-spacing, #8b949e
- Preço atual: "R$ 38,42" — Outfit, 2.5rem, cor teal #00e6d2
- Variação do dia: "+1,23%" com ícone TrendingUp em verde #2ea043 (ou vermelho #f85149 se negativo)
- Fundo: gradiente linear de #161a22 para rgba(0,230,210,0.05), borda rgba(255,255,255,0.08), border-radius 20px

CARD INDICADORES CHAVE:
- Título: "Indicadores Chave" com ícone de gráfico de barras
- Grid 2x2 de métricas:
  - P/L: 6.8
  - P/VP: 0.9
  - ROE: 18,4%
  - Dívida/EBITDA: 1.2
- Cada métrica: label pequeno uppercase #8b949e + valor grande Outfit bold #f0f3f8
- Fundo de cada item: #0f1115, borda rgba(255,255,255,0.05), border-radius 8px

CARD SCORE FUNDAMENTALISTA:
- Título: "Score Fundamentalista"
- Score visual: círculo grande (120px) com borda colorida (verde se ≥75, amarelo se 50-74, vermelho se <50)
  - Número dentro: "72" — Outfit, 2.5rem, bold
  - Label abaixo: "Bom"
- Barra de progresso horizontal abaixo do círculo mostrando 72/100
- Classificação por faixas: Fraco (0-24) | Regular (25-49) | Bom (50-74) | Excelente (75-100)
- Faixas coloridas: vermelho → amarelo → verde

=== COLUNA DIREITA ===

CARD DIAGNÓSTICO DA IA:
- Título: "Diagnóstico da IA" com ícone de atividade
- Bloco de veredito (fundo rgba(46,160,67,0.1), borda esquerda 4px verde):
  - Círculo de score à esquerda (80px): "72" + "Score"
  - Texto: "Veredito: Momento Favorável" — Outfit, 1.4rem
  - Parágrafo de conclusão: texto da IA explicando o ativo
- Grid 2 colunas de pontos:
  - Coluna "Pontos Fortes" (ícone TrendingUp verde):
    - Lista com ✓ verde: "ROE acima da média setorial", "Dividend Yield atrativo", "Baixo endividamento"
  - Coluna "Pontos de Atenção" (ícone AlertCircle vermelho):
    - Lista com ✕ vermelho: "P/L elevado para o setor", "Crescimento de receita desacelerado"
- Box "Momento Sugerido" (borda esquerda 2px roxo #8a2be2, fundo #0f1115):
  - Label: "Momento Sugerido" em roxo
  - Texto explicativo da IA sobre o momento atual

CARD HISTÓRICO DE PREÇOS (5 Anos):
- Título: "Histórico de Preços (5 Anos)" com ícone de cifrão
- Gráfico de área (AreaChart):
  - Linha teal #00e6d2, strokeWidth 2
  - Área preenchida com gradiente teal→transparente
  - Grid horizontal sutil rgba(255,255,255,0.1)
  - Eixo X: anos (2020, 2021, 2022, 2023, 2024)
  - Eixo Y: valores em R$
  - Tooltip dark: fundo #161a22, borda rgba(255,255,255,0.1), valor em teal
  - Altura: 300px

DISCLAIMER (abaixo do dashboard):
- Texto pequeno centralizado em #8b949e:
  "Esta análise é informativa e baseada em dados históricos públicos. Não constitui recomendação de investimento. A decisão final é sempre do usuário."

RESPONSIVIDADE:
- Mobile: coluna única, cards empilhados
- Tablet (768px): coluna única com cards lado a lado onde possível
- Desktop (992px+): grid 2 colunas
```

---

## PROMPT 3 — Tela de Loading

```
Crie uma tela de loading para o FundamentAI, exibida enquanto os dados do ativo são processados.

IDENTIDADE VISUAL: dark premium, fundo #0f1115, acentos teal #00e6d2.

LAYOUT (centralizado vertical e horizontal, altura 100vh):
- Spinner circular (50px): borda 3px, cor base rgba(255,255,255,0.08), topo #00e6d2, animação rotate 1s linear infinite
- Texto abaixo: "Processando Inteligência de Mercado..." — Outfit, 1.1rem, cor #00e6d2, animação pulse (opacity 0.6 → 1, 2s ease-in-out infinite)
- Subtexto opcional: "Coletando dados, calculando indicadores e gerando análise via IA" — Inter, 0.9rem, #8b949e

VARIAÇÃO PARA ETAPAS (opcional, versão mais elaborada):
- Mostrar progresso em 3 etapas com ícones:
  1. "Coletando dados da B3" — ícone database
  2. "Calculando indicadores" — ícone calculator/chart
  3. "Gerando análise com IA" — ícone brain/sparkles
- Etapa ativa: teal com glow; etapas concluídas: verde; etapas pendentes: #8b949e
- Linha conectora entre etapas

FUNDO: manter o gradiente radial sutil do produto (teal 3% canto esquerdo, roxo 3% canto direito)
```

---

## PROMPT 4 — Tela de Erro / Ticker Inativo

```
Crie a tela de feedback de erro para o FundamentAI, exibida quando o ticker não é encontrado ou está inativo.

IDENTIDADE VISUAL: dark premium, fundo #0f1115, acentos teal #00e6d2.

HEADER: igual ao padrão do produto.

CONTEÚDO CENTRALIZADO (abaixo do header):

CENÁRIO A — Ticker não encontrado:
- Card glassmorphism centralizado (máx 500px):
  - Ícone AlertCircle em vermelho #f85149 (48px)
  - Título: "Ticker não encontrado" — Outfit, 1.5rem
  - Mensagem: "O ticker 'XPTO3' não foi encontrado na base de dados. Verifique se o código está correto." — Inter, #8b949e
  - Botão "Tentar novamente" — fundo teal, texto escuro, border-radius 24px
  - Link "Ver tickers disponíveis" — texto teal, sem fundo

CENÁRIO B — Ticker inativo:
- Card glassmorphism centralizado (máx 500px):
  - Ícone com badge de aviso em amarelo #d29922 (48px)
  - Título: "Ativo Inativo" — Outfit, 1.5rem, cor #d29922
  - Mensagem: "O ativo 'XXXX3' está classificado como inativo na B3 e não possui dados suficientes para análise fundamentalista." — Inter, #8b949e
  - Informação adicional: "Ativos inativos possuem menos de 3 indicadores disponíveis e são excluídos automaticamente da análise."
  - Botão "Buscar outro ativo" — fundo teal, texto escuro

CENÁRIO C — Erro de conexão/API:
- Card glassmorphism centralizado (máx 500px):
  - Ícone de servidor/wifi off em vermelho (48px)
  - Título: "Erro ao carregar dados" — Outfit, 1.5rem
  - Mensagem técnica (se disponível): exibir em caixa de código pequena, fundo #0f1115, fonte monospace, cor #f85149
  - Botão "Tentar novamente" — fundo teal

TODOS OS CENÁRIOS:
- Fundo do card: glassmorphism rgba(255,255,255,0.03), borda rgba(255,255,255,0.08)
- Padding generoso (2rem)
- Border-radius 20px
- Sombra sutil
```

---

## PROMPT 5 — Componente: Card de Indicadores por Tipo de Ativo

```
Crie dois estados do componente "Indicadores Chave" para o FundamentAI, diferenciando Ações de FIIs.

IDENTIDADE VISUAL: dark premium, fundo #161a22, acentos teal #00e6d2.

ESTADO A — Ações (ex: PETR4):
- Badge "AÇÃO" no topo do card — fundo rgba(0,230,210,0.1), texto teal, border-radius 4px, uppercase
- Grid 2x3 de métricas (6 indicadores):
  - P/L: 6.8
  - P/VP: 0.9
  - ROE: 18,4%
  - Dívida/EBITDA: 1.2
  - Margem Líquida: 22,1%
  - Dividend Yield: 8,3%
- Cada métrica com tooltip de ajuda (ícone info pequeno) explicando o indicador

ESTADO B — FIIs (ex: HGLG11):
- Badge "FII" no topo do card — fundo rgba(138,43,226,0.1), texto roxo #8a2be2, border-radius 4px, uppercase
- Grid 2x2 de métricas (4 indicadores):
  - P/VP: 0.95
  - P/L: 12.3
  - Dividend Yield: 9,8%
  - Crescimento DY: +5,2%
- Nota informativa abaixo: "FIIs são avaliados com critérios específicos: foco em geração de renda e valor patrimonial."

AMBOS OS ESTADOS:
- Label de cada métrica: 0.75rem, uppercase, letter-spacing 0.5px, #8b949e
- Valor de cada métrica: 1.25rem, Outfit bold, #f0f3f8
- Fundo de cada item: #0f1115, borda rgba(255,255,255,0.05), border-radius 8px, padding 1rem
- Hover no item: borda rgba(0,230,210,0.2)
```

---

## PROMPT 6 — Versão Mobile (responsiva)

```
Adapte o dashboard do FundamentAI para mobile (375px de largura).

IDENTIDADE VISUAL: dark premium, fundo #0f1115, acentos teal #00e6d2.

HEADER MOBILE:
- Logo compacto à esquerda (ícone + "FundamentAI")
- Ícone de busca à direita (abre busca em overlay ao clicar)

BUSCA MOBILE (overlay):
- Tela cheia com fundo rgba(15,17,21,0.95)
- Input centralizado, largura 90%
- Teclado numérico/texto ativado automaticamente
- Botão "Cancelar" para fechar

LAYOUT MOBILE (coluna única, scroll vertical):
1. Card Hero do Ticker (ticker + preço + variação)
2. Card Score (círculo de score + classificação)
3. Card Indicadores (grid 2x2, scroll horizontal se necessário)
4. Card Diagnóstico da IA (veredito + pontos fortes/fracos empilhados)
5. Card Histórico de Preços (altura 200px)
6. Disclaimer

NAVEGAÇÃO BOTTOM (opcional):
- Barra fixa no rodapé com 3 ícones: Home, Busca, Histórico
- Fundo #161a22, borda superior rgba(255,255,255,0.08)
- Ícone ativo em teal

TIPOGRAFIA MOBILE:
- Ticker: 2rem (reduzido de 3rem)
- Preço: 1.8rem (reduzido de 2.5rem)
- Padding geral: 1rem (reduzido de 2rem)
```

---

## Notas para o Designer

- O disclaimer **"Esta análise é informativa e baseada em dados históricos públicos. Não constitui recomendação de investimento. A decisão final é sempre do usuário."** deve aparecer em **todas as telas** que exibam análises.
- O score usa 4 faixas: **Fraco** (0–24, vermelho), **Regular** (25–49, amarelo), **Bom** (50–74, verde claro), **Excelente** (75–100, verde).
- O sistema suporta dois tipos de ativo: **Ações** (badge teal) e **FIIs** (badge roxo) — os indicadores exibidos diferem entre os dois.
- A paleta é **exclusivamente dark** — não há modo claro.
- Componentes reutilizáveis: `ScoreCard`, `IndicatorTable`, `Chart`, `Verdict` (conforme estrutura em `frontend/src/components/`).