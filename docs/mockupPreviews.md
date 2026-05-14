# FundamentAI — Estrutura de Previews das Telas

Mapeamento das seções de design e seus respectivos arquivos de imagem localizados na pasta `docs/`.

---

## Tabela de Previews

| Seção | Arquivo | Descrição |
|---|---|---|
| Tela 1 — Home / Landing Page | `docs/tela-home.png` | Headline, barra de busca com chips de exemplo e 3 cards de features |
| Tela 2 — Dashboard de Análise | `docs/1.Analise.png` | Grid 2 colunas: indicadores, score, diagnóstico da IA e histórico de preços |
| Tela 3 — Loading | `docs/2.Loading.png` | Spinner animado e etapas de progresso (Coletar → Calcular → IA) |
| Tela 4 — Aviso / Erro | `docs/3.AvisoError.png` | Feedback para ticker não encontrado, ativo inativo ou erro de conexão |
| Tela 5 — Indicadores por Tipo de Ativo | `docs/4.Indicadores.png` | Card com badge AÇÃO (teal) ou FII (roxo) e indicadores específicos por tipo |
| Mockup Geral | `docs/gMock.jpeg` | Visão geral do produto com todas as telas e fluxo de navegação |

---

## Previews

### Tela 1 — Home / Landing Page

Ela segue a identidade visual black premium com prompt
de busca. 

![Tela 1 — Home](tela-home.png)

---

### Tela 2 — Dashboard de Análise

# Aqui está o mockup da tela do FundamentAI 
Ele segue a identidade visual white premium e estrutura de dashboard descrita no documento, com destaque para o Score Fundamentalista, indicadores chave e gráficos de evolução de preço.

![Tela 2 — Dashboard de Análise](1.Analise.png)

---

### Tela 3 — Loading

# Aqui está a Tela de Loading do FundamentAI 🎉

Ela traz o fundo dark premium com gradiente teal/roxo, o spinner circular animado e o texto “Processando Inteligência de Mercado...” centralizado, exatamente como definido no seu guia de design.

# Veja o mockup da tela de carregamento

![Tela 3 — Loading](2.Loading.png)

---

### Tela 4 — Aviso / Erro

Aqui está a Tela de Loading do FundamentAI 🎉


Aqui está a Tela de Erro / Ticker Inativo do FundamentAI ⚠️

Ela segue o estilo dark premium com fundo escuro e acentos em teal e vermelho, apresentando o ícone de alerta, o título “Ticker Inativo ou Indisponível”, e o botão “Voltar ao Dashboard”. O layout mantém o foco na clareza do feedback e na consistência visual com o restante do produto.

Visualizar mockup da tela de erro

![Tela 4 — Aviso / Erro](3.AvisoError.png)

---

### Tela 5 — Indicadores por Tipo de Ativo


# Card de Indicadores por Tipo de Ativo

Aqui está o Card de Indicadores por Tipo de Ativo do FundamentAI 💹

O design segue o estilo dark premium, com fundo escuro e acentos coloridos para cada métrica.

O topo exibe o título “Indicadores por Tipo de Ativo” e as abas de seleção (Ações, Fundos, FIIs, Cripto).

Cada card mostra um indicador com ícone, valor e descrição — como P/L, Dividend Yield, ROE e EV/EBITDA — em cores distintas para facilitar a leitura.

A aba ativa (Ações) tem destaque em teal, mantendo a identidade visual do produto.

# Visualizar mockup do card

![Tela 5 — Indicadores por Tipo de Ativo](4.Indicadores.png)

---

### Mockup Geral

![Mockup Geral](gMock.jpeg)

---

## Referências

- Script completo de prompts de design: [`TELA1.md`](../TELA1.md)
- Paleta de cores e identidade visual: ver seção "Paleta de Cores" em `TELA1.md`
- Componentes implementados: `frontend/src/components/` e `frontend/src/pages/`
