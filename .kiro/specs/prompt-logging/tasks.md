# Tasks: Prompt Logging

## 1. Configuração Inicial

### 1.1 Criar estrutura de diretórios
- [ ] Criar diretório `.kiro/hooks/` (se não existir)
- [ ] Criar diretório `.kiro/scripts/` (se não existir)
- [ ] Criar diretório `.kiro/prompt-logs/` (será criado automaticamente pelo script, mas pode ser criado manualmente)

### 1.2 Configurar dependências Python
- [ ] Adicionar `pytz>=2024.1` ao `requirements.txt` (ou criar arquivo se não existir)
- [ ] Documentar instalação de dependências no README

---

## 2. Implementação do Hook

### 2.1 Criar arquivo de hook
- [ ] Criar `.kiro/hooks/prompt-logger.json` com configuração do hook `promptSubmit`
- [ ] Validar sintaxe JSON
- [ ] Testar se hook é reconhecido pelo Kiro

---

## 3. Implementação do Script de Logging

### 3.1 Criar script Python base
- [ ] Criar `.kiro/scripts/log_prompt.py` com estrutura básica
- [ ] Adicionar shebang e encoding UTF-8
- [ ] Adicionar docstring de documentação

### 3.2 Implementar funções de coleta de metadados
- [ ] Implementar `get_git_branch()` - detecta branch atual via Git
- [ ] Implementar `get_git_user()` - obtém nome do usuário Git
- [ ] Implementar `get_brasilia_timestamp()` - gera timestamp em horário de Brasília
- [ ] Implementar tratamento de erros para cada função (fallback gracioso)

### 3.3 Implementar captura de conteúdo do prompt
- [ ] Implementar `get_prompt_content()` com múltiplas estratégias:
  - [ ] Tentar variável de ambiente `KIRO_PROMPT`
  - [ ] Tentar ler de stdin (se não for TTY)
  - [ ] Fallback para placeholder se não disponível
- [ ] Testar cada estratégia de captura

### 3.4 Implementar formatação de log
- [ ] Implementar `sanitize_branch_name()` - converte caracteres especiais em nomes válidos
- [ ] Implementar `format_log_entry()` - formata entrada no padrão Markdown
- [ ] Extrair título do prompt (primeiras 50 caracteres)
- [ ] Adicionar blocos de código para preservar formatação

### 3.5 Implementar persistência de logs
- [ ] Implementar `log_prompt()` - função principal
- [ ] Criar diretório `.kiro/prompt-logs/` se não existir
- [ ] Adicionar cabeçalho ao arquivo na primeira entrada
- [ ] Adicionar entrada formatada em modo append
- [ ] Implementar tratamento de erros gracioso (não bloquear Kiro)

### 3.6 Tornar script executável
- [ ] Adicionar permissões de execução: `chmod +x .kiro/scripts/log_prompt.py`
- [ ] Testar execução direta do script

---

## 4. Documentação

### 4.1 Criar documentação de uso
- [ ] Criar `docs/prompt-logging.md` com:
  - [ ] Visão geral da funcionalidade
  - [ ] Instruções de instalação
  - [ ] Instruções de uso
  - [ ] Exemplos de consulta de logs
  - [ ] Troubleshooting
  - [ ] Limitações conhecidas

### 4.2 Criar steering file
- [ ] Criar `.kiro/steering/prompt-logging.md` com:
  - [ ] Contexto da funcionalidade para o agente Kiro
  - [ ] Convenções de logging
  - [ ] Instruções para manutenção

### 4.3 Atualizar README principal
- [ ] Adicionar seção sobre Prompt Logging no README.md
- [ ] Incluir link para documentação detalhada
- [ ] Mencionar dependências (pytz)

### 4.4 Atualizar .gitignore (se necessário)
- [ ] Avaliar se logs devem ser versionados ou ignorados
- [ ] Adicionar entrada ao .gitignore se decisão for ignorar logs
- [ ] Documentar decisão no README

---

## 5. Testes

### 5.1 Testes manuais básicos
- [ ] Testar primeiro prompt em nova branch (arquivo criado com cabeçalho)
- [ ] Testar múltiplos prompts na mesma branch (append correto)
- [ ] Testar troca de branch (arquivos separados)
- [ ] Testar branch com caracteres especiais (sanitização correta)

### 5.2 Testes de edge cases
- [ ] Testar em branch sem Git configurado (fallback para "unknown")
- [ ] Testar com prompt vazio
- [ ] Testar com prompt muito longo (>1000 caracteres)
- [ ] Testar com caracteres especiais no prompt (UTF-8)

### 5.3 Testes de captura de conteúdo
- [ ] Validar se variável de ambiente `KIRO_PROMPT` está disponível
- [ ] Validar se stdin está disponível no contexto do hook
- [ ] Documentar resultado dos testes de captura

### 5.4 Testes de performance
- [ ] Medir tempo de execução do script (<100ms)
- [ ] Verificar que não bloqueia execução do Kiro

---

## 6. Validação e Ajustes

### 6.1 Validação de formato
- [ ] Verificar que logs são válidos em Markdown
- [ ] Verificar que diffs no Git são legíveis
- [ ] Verificar renderização no GitHub/GitLab

### 6.2 Validação de limitações
- [ ] Confirmar se conteúdo do prompt é capturado automaticamente
- [ ] Documentar limitações confirmadas
- [ ] Atualizar documentação com resultados dos testes

### 6.3 Code review
- [ ] Revisar código do script Python
- [ ] Revisar configuração do hook
- [ ] Revisar documentação

---

## 7. Entrega

### 7.1 Commit e versionamento
- [ ] Commit de todos os arquivos criados
- [ ] Seguir convenção de commits do projeto (Conventional Commits)
- [ ] Mensagem de commit descritiva

### 7.2 Documentação final
- [ ] Verificar que toda documentação está completa
- [ ] Verificar que exemplos estão corretos
- [ ] Verificar que limitações estão documentadas

### 7.3 Comunicação
- [ ] Informar equipe sobre nova funcionalidade
- [ ] Compartilhar documentação de uso
- [ ] Solicitar feedback inicial

---

## 8. Melhorias Futuras (Opcional)

### 8.1* Captura de resultados
- [ ] Implementar hook `agentStop` para capturar fim da execução
- [ ] Capturar resumo da resposta do agente
- [ ] Associar prompt → resultado no log

### 8.2* Interface de consulta
- [ ] Criar CLI para buscar logs: `kiro-logs search "keyword"`
- [ ] Implementar filtros por data, branch, usuário
- [ ] Exportação para JSON/CSV

### 8.3* Rotação de logs
- [ ] Implementar arquivamento automático de logs antigos
- [ ] Implementar compressão de arquivos grandes
- [ ] Configurar política de retenção

---

## Checklist de Conclusão

- [ ] Todos os arquivos criados e testados
- [ ] Documentação completa e revisada
- [ ] Testes manuais executados com sucesso
- [ ] Limitações documentadas
- [ ] README atualizado
- [ ] Commit realizado seguindo convenções do projeto
- [ ] Equipe informada sobre nova funcionalidade
