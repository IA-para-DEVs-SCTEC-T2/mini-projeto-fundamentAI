# Guia de Contribuição

Bem-vindo ao **FundamentAI**! Este guia orienta como contribuir para o projeto de forma organizada e consistente com os padrões da equipe.

---

## 📌 Visão Geral

O FundamentAI é uma plataforma que consolida dados financeiros públicos de empresas listadas na B3, aplica critérios objetivos de análise fundamentalista e entrega análises estruturadas com viés educativo — reduzindo a barreira de entrada para investidores iniciantes.

**Contribuições devem estar alinhadas com:**
- Objetivo educativo e informativo (não recomendações de investimento)
- Análise fundamentalista (não análise técnica/gráfica)
- Dados históricos públicos (não tempo real no MVP)
- Foco em ações e FIIs da B3

> ⚠️ **Disclaimer:** Este projeto não fornece recomendações de investimento. As análises são informativas e baseadas em dados históricos.

---

## 🛠️ Pré-requisitos

Antes de começar, certifique-se de ter instalado:

### Ferramentas Obrigatórias
- **Git** — controle de versão
- **Python 3.8+** — backend
- **Node.js 16+** e **npm/yarn** — frontend
- **Kiro IDE** (recomendado) — [kiro.dev](https://kiro.dev) no modo Auto

### Dependências do Backend
- `yfinance` — coleta de dados financeiros
- `fundamentus` — indicadores fundamentalistas da B3
- `pandas` — manipulação de dados
- `FastAPI` — framework da API REST
- `SQLAlchemy` — ORM para banco de dados
- `anthropic` — integração com API da Anthropic (Claude)

### Dependências do Frontend
- `React` — framework principal
- `Axios` — cliente HTTP
- `Recharts` ou `Chart.js` — visualização de gráficos
- `React Router` — navegação entre páginas

### Acessos Necessários
- **Chave da API da Anthropic** (`ANTHROPIC_API_KEY`) — para geração de análises via LLM
- **Acesso ao grupo da equipe no WhatsApp** — canal de comunicação

---

## ⚙️ Configuração do Ambiente de Desenvolvimento

### 1. Clone o Repositório

```bash
git clone <url-do-repositorio>
cd <nome-do-repositorio>
```

### 2. Configuração do Backend

```bash
cd backend

# Criar ambiente virtual Python
python -m venv venv

# Ativar ambiente virtual
# No macOS/Linux:
source venv/bin/activate
# No Windows:
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

**Configurar variáveis de ambiente:**

Crie um arquivo `.env` na raiz do projeto:

```env
ANTHROPIC_API_KEY=sua-chave-aqui
```

> ⚠️ **Nunca commite o arquivo `.env`** — ele já está no `.gitignore`

**Inicialização do banco de dados:**

*[A ser documentado — aguardando definição do script de setup]*

### 3. Configuração do Frontend

```bash
cd frontend

# Instalar dependências
npm install
# ou
yarn install
```

**Configurar variáveis de ambiente do frontend:**

*[A ser documentado — aguardando definição da URL da API backend]*

### 4. Execução Local

**Backend:**
```bash
# A ser documentado — comando para rodar FastAPI
# Exemplo esperado: uvicorn backend.api.main:app --reload
```

**Frontend:**
```bash
# A ser documentado — comando para rodar servidor de desenvolvimento
# Exemplo esperado: npm start ou yarn start
```

---

## 🌿 Fluxo de Trabalho com Branches

### Branches Principais

| Branch | Papel |
|---|---|
| `main` | Código estável em produção — **nunca recebe commits diretos** |
| `develop` | Branch de integração — **nunca recebe commits diretos** |

> Toda alteração passa por uma branch dedicada e Pull Request.

### Tipos de Branches de Trabalho

| Tipo | Quando usar | Base |
|---|---|---|
| `feature/` | Nova funcionalidade | `develop` |
| `bugfix/` | Correção de bug em desenvolvimento | `develop` |
| `hotfix/` | Correção urgente em produção | `main` |
| `release/` | Preparação de versão | `develop` |
| `chore/` | Manutenção sem impacto funcional | `develop` |
| `docs/` | Alterações exclusivas de documentação | `develop` |

### Convenção de Nomenclatura

```
<tipo>/<descricao-curta-em-portugues>
```

**Regras:**
- Letras minúsculas
- Hífens para separar palavras (sem espaços ou underscores)
- Nomes curtos e descritivos
- Idioma: português

**Exemplos reais do projeto:**

```bash
feature/coletor-yfinance
feature/dashboard-analise-ativo
bugfix/calculo-roe-incorreto
hotfix/crash-endpoint-ticker
chore/atualiza-dependencias-python
docs/atualiza-readme-stack
release/v0.1.0
```

### Criando uma Branch de Trabalho

```bash
# Atualizar develop
git checkout develop
git pull origin develop

# Criar e mudar para nova branch
git checkout -b feature/nome-da-funcionalidade
```

---

## 📝 Convenção de Commits

Adotamos o padrão **[Conventional Commits](https://www.conventionalcommits.org/)**.

### Formato

```
<tipo>(<escopo>): <descrição curta no imperativo>
```

### Tipos Permitidos

| Tipo | Quando usar |
|---|---|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `docs` | Alteração de documentação |
| `chore` | Manutenção, dependências, configurações |
| `refactor` | Reorganização de código sem alterar comportamento |
| `test` | Adição ou correção de testes |
| `style` | Formatação, espaçamento (sem impacto lógico) |
| `perf` | Melhoria de performance |
| `ci` | Alterações em pipelines de CI/CD |

### Escopos Baseados na Estrutura do Projeto

**Backend:**
- `collectors` — scripts de coleta de dados
- `processors` — cálculo de indicadores e scoring
- `api` — endpoints e rotas
- `prompts` — geração de prompts estruturados
- `etl` — pipeline de processamento
- `db` — modelos e repositórios de banco de dados

**Frontend:**
- `components` — componentes reutilizáveis
- `pages` — páginas da aplicação
- `services` — chamadas à API
- `hooks` — custom hooks React

### Exemplos Reais do Contexto

```bash
feat(collectors): adiciona coletor de dados via fundamentus
feat(api): implementa endpoint de consulta por ticker
feat(components): cria componente ScoreCard para exibição de score
fix(processors): corrige cálculo de margem líquida negativa
fix(frontend): corrige renderização do ScoreCard em mobile
docs: atualiza README com fluxo de dados da Anthropic API
chore: atualiza dependências do requirements.txt
refactor(prompts): separa template do builder de injeção de dados
test(processors): adiciona testes unitários para cálculo de ROE
```

### Regras de Commits

- ✅ Descrição no imperativo e em letras minúsculas
- ✅ Sem ponto final
- ✅ Máximo de 72 caracteres na primeira linha
- ✅ Commits atômicos — uma alteração lógica por commit
- ✅ Commits frequentes — não acumular dias de trabalho

### Commits Inválidos

❌ Mensagens genéricas:
```bash
git commit -m "fix"
git commit -m "update"
git commit -m "changes"
```

❌ Commits de merge manual (usar estratégia definida no PR)

❌ Acúmulo de múltiplas alterações lógicas não relacionadas

---

## 🔀 Abrindo um Pull Request

### Antes de Abrir o PR

Checklist obrigatório:

- [ ] Código testado localmente
- [ ] Sem conflitos com a branch de destino (`develop` ou `main`)
- [ ] Commits seguem a convenção de Conventional Commits
- [ ] Documentação atualizada (se aplicável)
- [ ] Nenhum segredo (chaves de API, senhas) foi commitado

### Título do PR

Seguir o mesmo padrão de Conventional Commits:

```
feat(collectors): adiciona integração com API do Banco Central
fix(api): corrige timeout no endpoint de análise
```

### Branch de Destino

| Tipo de branch | Destino |
|---|---|
| `feature/`, `bugfix/`, `chore/`, `docs/` | `develop` |
| `hotfix/` | `main` (e depois sincronizar com `develop`) |
| `release/` | `main` |

### Template de Descrição

Incluir obrigatoriamente:

```markdown
## O que foi feito
[Resumo claro da alteração]

## Por que foi feito
[Contexto ou problema resolvido]

## Como testar
[Passos para validar localmente]

## Issue relacionada
Closes #123
<!-- ou -->
Ref #123
```

### Processo de Revisão

- Todo PR deve ter **ao menos 1 aprovação** antes do merge
- **Você não pode aprovar seu próprio PR**
- Comentários de revisão devem ser resolvidos antes do merge
- O autor do PR é responsável por resolver conflitos
- Use os comentários do PR para discussões sobre o trabalho em andamento

### Estratégia de Merge

| Tipo de branch | Destino | Estratégia |
|---|---|---|
| `feature/`, `bugfix/`, `chore/`, `docs/` | `develop` | **Squash merge** |
| `release/` | `main` | **Merge commit** |
| `hotfix/` | `main` e `develop` | **Merge commit** |

**Squash merge** consolida todos os commits da branch em um único commit limpo no histórico.

---

## 🐛 Reportando Bugs e Sugerindo Melhorias

### Como Abrir uma Issue

**Para bugs:**

```markdown
**Descrição do problema**
[Descrição clara do bug]

**Passos para reproduzir**
1. [Primeiro passo]
2. [Segundo passo]
3. [...]

**Comportamento esperado**
[O que deveria acontecer]

**Comportamento observado**
[O que realmente aconteceu]

**Contexto**
- Versão: [ex: v0.1.0]
- Ambiente: [ex: desenvolvimento local, produção]
- Logs relevantes: [se aplicável]
```

**Para melhorias:**

```markdown
**Descrição da melhoria**
[Descrição clara da funcionalidade ou melhoria proposta]

**Motivação**
[Por que isso seria útil]

**Proposta de implementação** (opcional)
[Como você imagina que isso poderia ser implementado]
```

### Escopo de Contribuições Aceitas

**Dentro do MVP:**
- ✅ Ações e FIIs listados na B3
- ✅ Análise fundamentalista
- ✅ Dados históricos
- ✅ Score fundamentalista
- ✅ Visualização de gráficos e comparação setorial
- ✅ Explicação simplificada de indicadores

**Fora do escopo atual:**
- ❌ Análise técnica/gráfica
- ❌ Dados em tempo real
- ❌ Outros mercados (ex: EUA)
- ❌ Machine Learning para scoring avançado

> Sugestões fora do escopo atual podem ser consideradas para evoluções futuras.

---

## ❌ O que NÃO fazer

### Branches e Versionamento

- ❌ Commit direto em `main` ou `develop`
- ❌ Force push em `main` ou `develop`
- ❌ Aprovar o próprio Pull Request
- ❌ Branches abertas por mais de uma semana sem atividade
- ❌ Deletar branches antes do merge ser concluído

### Commits

- ❌ Mensagens genéricas ou fora do padrão Conventional Commits
- ❌ Acumular múltiplas alterações lógicas em um único commit
- ❌ Commits de merge manual (usar a estratégia definida)

### Segurança

- ❌ Commitar segredos (chaves de API, senhas, tokens)
  - Use `.env` e verifique se está no `.gitignore`
- ❌ Expor `ANTHROPIC_API_KEY` no código
  - Sempre usar variável de ambiente

### Arquitetura e Código

- ❌ Hardcoded de prompts nas rotas da API
  - Prompts devem ficar em `backend/prompts/`
- ❌ Lógica de negócio em `backend/api/` ou `backend/etl/`
  - Lógica de negócio deve ficar em `backend/processors/`
- ❌ Componentes do frontend chamando a API diretamente
  - Usar abstração em `frontend/services/`
- ❌ Misturar responsabilidades em um único módulo
  - Seguir a separação definida em `.kiro/steering/structure.md`

### Convenções de Código

**Backend (Python):**
- ❌ Usar `camelCase` — usar `snake_case`
- ❌ Nomes de arquivos e pastas em `PascalCase` — usar `snake_case`

**Frontend (React):**
- ❌ Componentes em `snake_case` — usar `PascalCase`
- ❌ Serviços e utilitários em `PascalCase` — usar `camelCase`

---

## 💬 Dúvidas?

### Canal de Comunicação

- **WhatsApp da equipe** — canal principal para dúvidas gerais e discussões
- **Comentários em Pull Requests** — discussões sobre trabalhos em andamento

### Documentação de Referência

- **`README.md`** — visão geral do projeto
- **`GITFLOW.md`** — fluxo de versionamento detalhado
- **`.kiro/steering/`** — contexto completo do projeto:
  - `product.md` — visão do produto e escopo
  - `structure.md` — organização de diretórios
  - `tech.md` — stack tecnológica e decisões de arquitetura
  - `gitflow.md` — estratégia de branches e convenções

---

**Obrigado por contribuir com o FundamentAI! 🚀**
