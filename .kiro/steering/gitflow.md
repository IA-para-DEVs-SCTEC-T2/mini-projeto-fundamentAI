# Git Flow

## Objetivo

Padronizar o fluxo de versionamento Git adotado neste repositório, garantindo um histórico limpo, rastreável e compreensível para todos os colaboradores. As regras aqui definidas se aplicam tanto ao backend (Python) quanto ao frontend (React) do Analisador Fundamentalista de Ações da B3.

---

## Branches Principais

| Branch | Papel |
|---|---|
| `main` | Código estável e testado — reflete o que está em produção. Nunca recebe commits diretos. |
| `develop` | Branch de integração. Todas as features concluídas são mergeadas aqui antes de ir para `main`. |

> Nenhum commit deve ser feito diretamente em `main` ou `develop`. Toda alteração passa por uma branch dedicada e PR.

---

## Branches de Trabalho

| Tipo | Quando usar |
|---|---|
| `feature/` | Nova funcionalidade (ex: novo coletor, nova página no frontend) |
| `bugfix/` | Correção de bug identificado em `develop` |
| `hotfix/` | Correção urgente de bug em produção — parte de `main`, volta para `main` e `develop` |
| `release/` | Preparação de versão antes de ir para `main` (ajustes finais, bump de versão, changelog) |
| `chore/` | Tarefas de manutenção sem impacto funcional (dependências, configs, CI) |
| `docs/` | Alterações exclusivas de documentação |

---

## Convenção de Nomes de Branches

```
feature/nome-da-funcionalidade
bugfix/descricao-do-ajuste
hotfix/descricao-do-problema
release/v1.2.0
chore/descricao-da-tarefa
docs/descricao-da-documentacao
```

**Regras:**
- Letras minúsculas e hífens — sem espaços, underscores ou caracteres especiais
- Nomes curtos e descritivos
- Usar o idioma do projeto (português, manter consistência)

**Exemplos práticos:**
```
feature/coletor-yfinance
feature/dashboard-analise-ativo
bugfix/calculo-roe-incorreto
hotfix/crash-endpoint-ticker
chore/atualiza-dependencias-python
docs/atualiza-readme-stack
release/v0.1.0
```

---

## Convenção de Commits

Adotar o padrão [Conventional Commits](https://www.conventionalcommits.org/).

### Formato

```
<tipo>(<escopo opcional>): <descrição curta no imperativo>
```

### Tipos

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

### Exemplos

```
feat(collectors): adiciona coletor de dados via fundamentus
feat(api): implementa endpoint de consulta por ticker
fix(processors): corrige cálculo de margem líquida negativa
fix(frontend): corrige renderização do ScoreCard em mobile
docs: atualiza README com fluxo de dados da Anthropic API
chore: atualiza dependências do requirements.txt
refactor(prompts): separa template do builder de injeção de dados
test(processors): adiciona testes unitários para cálculo de ROE
```

**Regras:**
- Descrição no imperativo e em letras minúsculas
- Sem ponto final
- Máximo de 72 caracteres na primeira linha
- Commits atômicos — uma alteração lógica por commit

---

## Pull Requests

### Título
Seguir o mesmo padrão de Conventional Commits:
```
feat(collectors): adiciona integração com API do Banco Central
fix(api): corrige timeout no endpoint de análise
```

### Descrição
Incluir obrigatoriamente:

- **O que foi feito** — resumo da alteração
- **Por que foi feito** — contexto ou problema resolvido
- **Como testar** — passos para validar localmente
- **Issue relacionada** — `Closes #123` ou `Ref #123`, quando existir

### Antes de abrir o PR
- [ ] Código testado localmente
- [ ] Sem conflitos com a branch de destino (`develop` ou `main`)
- [ ] Commits seguem a convenção definida
- [ ] Documentação atualizada, se necessário

### Revisão
- Todo PR deve ter ao menos **1 aprovação** antes do merge
- **Nenhum membro da equipe pode aprovar seu próprio PR**
- Comentários de revisão devem ser resolvidos antes do merge
- O autor do PR é responsável por resolver conflitos

---

## Merge Strategy

### Recomendação padrão: **Squash Merge**

Para branches `feature/`, `bugfix/`, `chore/` e `docs/` mergeando em `develop`:
- Usar **squash merge** — consolida todos os commits da branch em um único commit limpo no histórico de `develop`
- O título do commit resultante deve seguir a convenção de Conventional Commits

Para branches `release/` mergeando em `main`:
- Usar **merge commit** — preserva o contexto da release no histórico

Para branches `hotfix/` mergeando em `main` e `develop`:
- Usar **merge commit** — mantém rastreabilidade da correção urgente

| Tipo de branch | Destino | Estratégia |
|---|---|---|
| `feature/`, `bugfix/`, `chore/`, `docs/` | `develop` | Squash merge |
| `release/` | `main` | Merge commit |
| `hotfix/` | `main` e `develop` | Merge commit |

---

## Releases

Adotar **versionamento semântico** ([SemVer](https://semver.org/)): `MAJOR.MINOR.PATCH`

| Incremento | Quando usar |
|---|---|
| `MAJOR` | Mudança incompatível com versão anterior |
| `MINOR` | Nova funcionalidade compatível com versão anterior |
| `PATCH` | Correção de bug compatível com versão anterior |

### Fluxo de release

1. Criar branch `release/vX.Y.Z` a partir de `develop`
2. Realizar ajustes finais (bump de versão, atualização de changelog)
3. Abrir PR de `release/vX.Y.Z` → `main`
4. Após merge em `main`, criar **tag** com a versão:
   ```
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```
5. Mergear `main` de volta em `develop` para sincronizar

### Changelog
Manter um arquivo `CHANGELOG.md` na raiz do projeto, atualizado a cada release com as alterações agrupadas por tipo (`feat`, `fix`, etc.).

---

## Boas Práticas

- **Branches de curta duração** — feature branches devem ser mergeadas e deletadas assim que concluídas; evitar branches abertas por mais de uma semana sem atividade
- **Commits frequentes e atômicos** — commitar uma alteração lógica por vez, não acumular dias de trabalho em um único commit
- **Nunca fazer force push em `main` ou `develop`** — apenas em branches pessoais de trabalho, e com cautela
- **Deletar branches após o merge** — manter o repositório limpo
- **Sincronizar com `develop` regularmente** — fazer rebase ou merge de `develop` na feature branch para evitar conflitos grandes no final
- **Não commitar segredos** — chaves de API (ex: `ANTHROPIC_API_KEY`), senhas ou tokens nunca devem ir para o repositório; usar `.env` com `.gitignore` configurado
