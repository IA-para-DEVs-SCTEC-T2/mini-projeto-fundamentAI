# Requisitos: Prompt Logging

## Visão Geral

Sistema de registro automático de prompts executados no Kiro, organizado por branch Git, para manter rastreabilidade completa das interações durante o desenvolvimento.

---

## Problema

Atualmente não existe rastreabilidade das interações com o Kiro durante o desenvolvimento. Isso dificulta:

- Auditar decisões tomadas pelo agente em cada branch
- Entender o histórico de comandos executados
- Revisar o contexto de mudanças em code reviews
- Documentar o processo de desenvolvimento
- Compartilhar conhecimento entre membros da equipe

---

## Objetivos

- Registrar automaticamente todos os prompts executados no Kiro
- Organizar logs por branch Git
- Manter histórico incremental e versionável
- Minimizar atrito no fluxo de trabalho do desenvolvedor
- Preservar contexto das interações para auditoria futura

---

## Requisitos Funcionais

### RF01: Captura Automática de Prompts
**Prioridade:** Alta

O sistema deve capturar automaticamente cada prompt submetido ao Kiro, incluindo:
- Conteúdo completo do prompt
- Timestamp da execução (fuso horário de Brasília)
- Branch Git ativa no momento da execução
- Identificação do responsável (nome do usuário Git)

**Critérios de Aceitação:**
- Prompt é registrado imediatamente após submissão
- Nenhuma ação manual é necessária do desenvolvedor
- Dados são capturados de forma consistente

### RF02: Organização por Branch
**Prioridade:** Alta

Os logs devem ser organizados por branch Git, seguindo a estrutura:
```
.kiro/prompt-logs/<branch-name>.md
```

**Critérios de Aceitação:**
- Cada branch tem seu próprio arquivo de log
- Nome do arquivo corresponde exatamente ao nome da branch
- Logs de branches diferentes não se misturam
- Arquivo é criado automaticamente na primeira execução em uma branch

### RF03: Formato Estruturado de Log
**Prioridade:** Alta

Cada entrada de log deve seguir o formato:

```markdown
## Prompt: <título ou identificador>
- Responsável: <nome do usuário Git>
- Branch: <nome-da-branch>
- Data/hora: <YYYY-MM-DD HH:mm:ss> (Brasília)

### Prompt original
<conteúdo completo do prompt>

---
```

**Critérios de Aceitação:**
- Formato é consistente em todas as entradas
- Timestamp usa fuso horário de Brasília (UTC-3)
- Conteúdo do prompt é preservado sem alterações
- Separador visual entre entradas

### RF04: Histórico Incremental
**Prioridade:** Alta

Novos prompts devem ser adicionados ao final do arquivo existente, preservando o histórico completo.

**Critérios de Aceitação:**
- Logs anteriores nunca são sobrescritos
- Ordem cronológica é mantida
- Arquivo cresce incrementalmente

### RF05: Versionamento Git
**Prioridade:** Alta

Os arquivos de log devem ser versionáveis no Git.

**Critérios de Aceitação:**
- Arquivos `.md` são rastreados pelo Git
- Formato é legível em diffs
- Não contém dados binários ou sensíveis

### RF06: Hook de Captura
**Prioridade:** Alta

Implementar um hook do Kiro que intercepta o evento `promptSubmit` para capturar automaticamente os prompts.

**Critérios de Aceitação:**
- Hook é ativado em todo `promptSubmit`
- Hook executa script de logging
- Falhas no hook não bloqueiam a execução do prompt

### RF07: Script de Logging
**Prioridade:** Alta

Script Python que:
- Detecta a branch Git atual
- Obtém nome do usuário Git
- Formata timestamp em horário de Brasília
- Cria/atualiza arquivo de log da branch
- Adiciona entrada formatada ao arquivo

**Critérios de Aceitação:**
- Script é executável independentemente
- Trata erros graciosamente
- Cria diretórios necessários automaticamente
- Não falha se Git não estiver configurado

---

## Requisitos Não-Funcionais

### RNF01: Performance
O registro de prompts não deve adicionar latência perceptível à execução.

**Critério:** Overhead < 100ms por prompt

### RNF02: Confiabilidade
Falhas no sistema de logging não devem interromper o fluxo de trabalho normal.

**Critério:** Erros são logados mas não bloqueiam a execução do Kiro

### RNF03: Privacidade
Não armazenar dados sensíveis desnecessários.

**Critério:** Apenas informações essenciais são registradas (sem tokens, senhas, chaves de API)

### RNF04: Manutenibilidade
Código simples e bem documentado.

**Critério:** Documentação clara de uso e limitações

---

## Restrições e Limitações

### Limitação Técnica: Kiro não expõe APIs públicas
O Kiro não possui APIs públicas para captura automática de prompts. A solução depende de:
- Hooks do Kiro (eventos `promptSubmit`)
- Execução de comandos shell via hook

### Limitação: Conteúdo do Prompt
O hook `promptSubmit` pode não ter acesso direto ao conteúdo completo do prompt. Alternativas:
1. Capturar via variáveis de ambiente (se disponível)
2. Solicitar ao usuário copiar o prompt manualmente (alto atrito)
3. Registrar apenas metadados (timestamp, branch, responsável)

**Decisão:** Implementar solução com hooks e validar se o conteúdo do prompt está acessível. Se não estiver, documentar a limitação e registrar apenas metadados.

### Limitação: Resumo do Resultado
Capturar o "resumo do resultado gerado pelo Kiro" requer:
- Hook `agentStop` para capturar fim da execução
- Acesso à resposta do agente (pode não estar disponível)

**Decisão:** Implementar em fase futura se viável. MVP foca em captura de prompts.

---

## Casos de Uso

### UC01: Desenvolvedor Executa Prompt em Feature Branch
1. Desenvolvedor está na branch `feature/nova-funcionalidade`
2. Desenvolvedor envia prompt: "Implemente autenticação JWT"
3. Hook `promptSubmit` é acionado automaticamente
4. Script de logging:
   - Detecta branch: `feature/nova-funcionalidade`
   - Obtém usuário Git: `João Silva`
   - Gera timestamp: `2026-04-30 14:35:22`
   - Cria/atualiza `.kiro/prompt-logs/feature-nova-funcionalidade.md`
   - Adiciona entrada formatada
5. Desenvolvedor continua trabalhando normalmente

### UC02: Troca de Branch
1. Desenvolvedor está na branch `feature/branch-a` com logs existentes
2. Desenvolvedor troca para `feature/branch-b`
3. Desenvolvedor envia novo prompt
4. Sistema cria/atualiza `.kiro/prompt-logs/feature-branch-b.md`
5. Logs de `branch-a` permanecem intactos

### UC03: Code Review
1. Revisor abre PR de `feature/nova-funcionalidade`
2. Revisor consulta `.kiro/prompt-logs/feature-nova-funcionalidade.md`
3. Revisor entende contexto das decisões tomadas
4. Revisor faz comentários mais informados

---

## Critérios de Sucesso

- [ ] Prompts são registrados automaticamente sem intervenção manual
- [ ] Logs são organizados por branch
- [ ] Formato é consistente e legível
- [ ] Histórico é preservado incrementalmente
- [ ] Arquivos são versionáveis no Git
- [ ] Documentação de uso está clara
- [ ] Limitações estão documentadas

---

## Dependências

- Git instalado e configurado
- Python 3.8+ (para script de logging)
- Kiro com suporte a hooks

---

## Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Hook não tem acesso ao conteúdo do prompt | Alta | Alto | Documentar limitação; registrar apenas metadados |
| Falha no script bloqueia execução | Média | Alto | Tratar erros graciosamente; não bloquear Kiro |
| Logs crescem indefinidamente | Baixa | Médio | Documentar estratégia de rotação (fase futura) |
| Conflitos de merge em logs | Média | Baixo | Formato incremental facilita resolução |

---

## Fases de Implementação

### Fase 1: MVP (Escopo Atual)
- Hook `promptSubmit`
- Script de logging básico
- Captura de metadados (branch, usuário, timestamp)
- Tentativa de captura de conteúdo do prompt
- Documentação de uso

### Fase 2: Melhorias Futuras
- Hook `agentStop` para capturar resultados
- Resumo automático de respostas
- Interface de consulta de logs
- Rotação automática de logs antigos
- Integração com ferramentas de análise

---

## Entregáveis

1. **Hook do Kiro:** `.kiro/hooks/prompt-logger.json`
2. **Script de logging:** `.kiro/scripts/log_prompt.py`
3. **Documentação de uso:** `docs/prompt-logging.md`
4. **Steering file:** `.kiro/steering/prompt-logging.md`
5. **Atualização do .gitignore:** Garantir que logs não sejam ignorados (ou configurar conforme política do projeto)
6. **README atualizado:** Seção sobre prompt logging

---

## Referências

- [Kiro Hooks Documentation](https://kiro.dev/docs/hooks)
- Git Flow do projeto: `.kiro/steering/gitflow.md`
- Estrutura do projeto: `.kiro/steering/structure.md`
