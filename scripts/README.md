# Scripts de Automação

Este diretório contém scripts de automação utilizados no projeto FundamentAI.

## 📜 Scripts Disponíveis

### `create_all_issues.py`

Script Python para criar labels no repositório GitHub.

**Uso:**
```bash
python3 scripts/create_all_issues.py
```

**Descrição:**
- Cria todas as labels necessárias para categorizar as issues do projeto
- Labels incluem: setup, backend, frontend, database, collectors, etc.

---

### `create_issues.sh`

Script Bash para criar as primeiras issues do projeto (1-5).

**Uso:**
```bash
bash scripts/create_issues.sh
```

**Descrição:**
- Cria as issues iniciais de setup e coletores
- Utiliza a GitHub CLI (`gh`)

---

### `create_remaining_issues.py`

Script Python para criar issues restantes do projeto.

**Uso:**
```bash
python3 scripts/create_remaining_issues.py
```

**Descrição:**
- Cria issues de processadores, API, frontend, testes e documentação
- Utiliza a GitHub CLI (`gh`)

---

## 🔧 Pré-requisitos

- **GitHub CLI (`gh`)** instalado e autenticado
- **Python 3.8+** para scripts Python
- **Bash** para scripts shell

### Instalação do GitHub CLI

**macOS:**
```bash
brew install gh
```

**Linux:**
```bash
# Debian/Ubuntu
sudo apt install gh

# Fedora/RHEL
sudo dnf install gh
```

**Autenticação:**
```bash
gh auth login
gh auth refresh -s project  # Adicionar scope para projects
```

---

## 📝 Notas

- Estes scripts foram utilizados para criar as 29 issues iniciais do projeto
- As issues foram automaticamente vinculadas ao [Project 8](https://github.com/orgs/IA-para-DEVs-SCTEC-T2/projects/8)
- Os scripts seguem as convenções definidas em `.kiro/steering/gitflow.md`

---

## 🎯 Contexto

Estes scripts foram criados durante a **FASE 2** do processo de criação de issues, seguindo a metodologia:

1. **FASE 1**: Análise e proposta de backlog (aprovada pelo usuário)
2. **FASE 2**: Criação automatizada das issues no GitHub

Todas as issues incluem:
- Título no formato Conventional Commits
- Contexto ancorado no README e steering files
- Escopo detalhado e atômico
- Critérios de aceite verificáveis
- Dependências explícitas
- Referências aos documentos do projeto
