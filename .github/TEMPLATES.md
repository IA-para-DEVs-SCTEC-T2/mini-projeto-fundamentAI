# Templates do GitHub

Este diretório contém templates para Issues e Pull Requests do projeto FundamentAI.

## 📋 Templates de Issues

### 🚀 Feature Request (`feature.yml`)
Use para propor novas funcionalidades.

**Quando usar:**
- Adicionar nova funcionalidade ao sistema
- Implementar novo componente ou módulo
- Expandir capacidades existentes

**Campos obrigatórios:**
- Contexto
- Escopo
- Critérios de Aceite
- Categoria
- Prioridade

---

### 🐛 Bug Report (`bug_report.yml`)
Use para reportar bugs ou comportamentos incorretos.

**Quando usar:**
- Sistema não funciona como esperado
- Erro ou crash
- Comportamento incorreto

**Campos obrigatórios:**
- Descrição do Bug
- Passos para Reproduzir
- Comportamento Esperado
- Comportamento Atual
- Severidade
- Componente Afetado

---

### 📚 Documentation (`documentation.yml`)
Use para melhorias ou adições à documentação.

**Quando usar:**
- Criar nova documentação
- Atualizar documentação existente
- Melhorar clareza da documentação

**Campos obrigatórios:**
- Contexto
- Escopo
- Tipo de Documentação

---

### 🔧 Chore/Maintenance (`chore.yml`)
Use para tarefas de manutenção, configuração ou refatoração.

**Quando usar:**
- Atualizar dependências
- Configurar ferramentas
- Refatorar código
- Melhorar CI/CD
- Tarefas de limpeza

**Campos obrigatórios:**
- Contexto
- Escopo
- Critérios de Aceite
- Tipo de Tarefa

---

### 💬 General Issue (`general.yml`)
Use para issues que não se encaixam nas outras categorias.

**Quando usar:**
- Discussões gerais
- Questões que não se encaixam em outras categorias
- Propostas de melhoria geral

---

## 📝 Template de Pull Request

O template de PR (`pull_request_template.md`) é aplicado automaticamente ao criar uma nova Pull Request.

**Seções do template:**
- **Contexto**: Por que a mudança é necessária
- **O que foi feito**: Descrição das alterações
- **Como testar**: Passos para validação
- **Dependências**: Issues relacionadas
- **Referências**: Links para documentação
- **Checklist**: Itens de verificação
- **Screenshots/Logs**: Evidências visuais (opcional)

---

## 🎯 Boas Práticas

### Para Issues

1. **Seja específico**: Descreva claramente o problema ou funcionalidade
2. **Forneça contexto**: Explique por que a issue é necessária
3. **Defina critérios de aceite**: Como validar que está completo
4. **Referencie documentação**: Link para steering files relevantes
5. **Use labels apropriadas**: Facilita organização e busca

### Para Pull Requests

1. **Título descritivo**: Use Conventional Commits (feat:, fix:, docs:, chore:)
2. **Descrição completa**: Explique o que foi feito e por quê
3. **Passos de teste**: Facilite a revisão
4. **Link issues**: Use "Closes #123" para fechar automaticamente
5. **Checklist completo**: Marque todos os itens antes de solicitar revisão

---

## 📚 Referências

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Flow do Projeto](../.kiro/steering/gitflow.md)
- [Estrutura do Projeto](../.kiro/steering/structure.md)
- [Stack Tecnológica](../.kiro/steering/tech.md)

---

## 🔄 Atualizando Templates

Para atualizar os templates:

1. Edite os arquivos `.yml` em `.github/ISSUE_TEMPLATE/`
2. Edite `pull_request_template.md` para o template de PR
3. Teste criando uma nova issue/PR
4. Commit e push das alterações

**Nota**: Mudanças nos templates só afetam novas issues/PRs, não as existentes.
