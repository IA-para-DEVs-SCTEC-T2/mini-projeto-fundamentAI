# Estrutura do Projeto

Organização de diretórios baseada na arquitetura definida no README: backend Python (coleta, processamento, ETL e API) e frontend React (dashboard e visualizações).

---

## Estrutura de Diretórios

```
/
├── backend/
│   ├── collectors/          # Scripts de coleta de dados por fonte
│   │   ├── yfinance.py
│   │   ├── fundamentus.py
│   │   └── bacen.py         # SELIC e IPCA via API do Banco Central
│   │
│   ├── processors/          # Processamento e cálculo de indicadores
│   │   ├── indicators.py    # ROE, ROIC, margem líquida, P/L, P/VP, etc.
│   │   ├── scoring.py       # Lógica de score fundamentalista
│   │   └── comparator.py    # Comparação setorial
│   │
│   ├── etl/                 # Orquestração do pipeline diário
│   │   └── pipeline.py      # ETL pós-fechamento do mercado
│   │
│   ├── prompts/             # Geração de prompts estruturados para análise
│   │   └── builder.py       # Monta o prompt com dados + indicadores + macro
│   │
│   ├── api/                 # API que serve os dados ao frontend
│   │   ├── routes/
│   │   │   ├── ticker.py    # Endpoint de consulta por ticker
│   │   │   └── analysis.py  # Endpoint de análise e veredito
│   │   └── main.py          # Entry point da API
│   │
│   ├── db/                  # Modelos e acesso ao banco de dados
│   │   ├── models.py
│   │   └── repository.py
│   │
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/      # Componentes reutilizáveis
│   │   │   ├── ScoreCard/
│   │   │   ├── IndicatorTable/
│   │   │   ├── Chart/
│   │   │   └── Verdict/
│   │   │
│   │   ├── pages/           # Páginas da aplicação
│   │   │   ├── Home/        # Busca por ticker
│   │   │   └── Analysis/    # Dashboard de análise do ativo
│   │   │
│   │   ├── services/        # Chamadas à API do backend
│   │   ├── hooks/           # Custom hooks React
│   │   ├── utils/           # Funções auxiliares
│   │   └── App.jsx
│   │
│   ├── public/
│   └── package.json
│
├── docs/                    # Documentação do projeto
├── .kiro/                   # Configurações e steering do Kiro
└── README.md
```

---

## Responsabilidades por Camada

### `backend/collectors/`
Cada arquivo é responsável por uma fonte de dados específica. Isolar por fonte facilita manutenção e substituição independente.

### `backend/processors/`
Lógica pura de cálculo e scoring. Sem dependência de banco ou API — facilita testes unitários.

### `backend/etl/`
Orquestra a execução diária: coleta → processa → persiste. Deve rodar pós-fechamento do mercado.

### `backend/prompts/`
Monta o prompt estruturado que será enviado para geração da análise. Centraliza o formato de entrada esperado.

### `backend/api/`
Expõe os dados processados ao frontend via HTTP. Não contém lógica de negócio — apenas roteamento e serialização.

### `frontend/components/`
Componentes visuais reutilizáveis: ScoreCard, tabela de indicadores, gráficos, veredito. Cada componente em sua própria pasta com estilos e testes.

### `frontend/pages/`
Duas páginas principais no MVP: busca por ticker (Home) e dashboard de análise (Analysis).

### `frontend/services/`
Abstração das chamadas HTTP ao backend. Nenhum componente deve chamar a API diretamente.

---

## Convenções

- Nomes de arquivos e pastas em `snake_case` no backend (Python)
- Nomes de componentes e pastas em `PascalCase` no frontend (React)
- Nomes de arquivos de serviço e utilitários em `camelCase` no frontend
- Cada módulo do backend deve ter responsabilidade única e bem definida
- Lógica de negócio fica em `processors/`, nunca em `api/` ou `etl/`
