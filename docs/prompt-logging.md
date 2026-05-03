# 📝 Prompt Logging - Documentação de Uso

## Visão Geral

O sistema de **Prompt Logging** registra automaticamente todos os prompts executados no Kiro, organizando-os por branch Git. Isso permite rastreabilidade completa das interações com o agente durante o desenvolvimento, facilitando auditorias, code reviews e documentação do processo de desenvolvimento.

### Benefícios

- ✅ **Rastreabilidade completa** - Histórico de todas as interações com o Kiro
- ✅ **Organização por branch** - Logs isolados para cada branch de trabalho
- ✅ **Zero atrito** - Funciona automaticamente, sem ação manual
- ✅ **Versionável** - Arquivos Markdown rastreados pelo Git
- ✅ **Auditável** - Facilita code reviews e compartilhamento de conhecimento

---

## Como Funciona

```
Você envia um prompt → Kiro intercepta → Script registra → Log salvo
```

O sistema utiliza um **hook do Kiro** que intercepta o evento `promptSubmit` e executa automaticamente um script Python que:

1. Detecta a branch Git atual
2. Obtém o nome do usuário Git
3. Gera timestamp no horário de Brasília
4. Tenta capturar o conteúdo do prompt
5. Salva tudo em `.kiro/prompt-logs/<branch-name>.md`

**Importante:** Todo o processo é automático e transparente. Você não precisa fazer nada!

---

## Instalação

### Pré-requisitos

- Python 3.8 ou superior
- Git instalado e configurado
- Kiro instalado

### Passo 1: Instalar Dependências

O sistema requer a biblioteca `pytz` para manipulação de fusos horários:

```bash
pip install -r requirements.txt
```

Ou instale diretamente:

```bash
pip install pytz
```

### Passo 2: Verificar Estrutura

Certifique-se de que os seguintes arquivos existem no projeto:

```
.kiro/
├── hooks/
│   └── prompt-logger.json      # Hook de captura
└── scripts/
    └── log_prompt.py           # Script de logging
```

### Passo 3: Reiniciar o Kiro (se necessário)

Se você acabou de adicionar o hook, pode ser necessário reiniciar o Kiro para que ele seja carregado.

### Verificação

Para verificar se está funcionando:

1. Execute qualquer prompt no Kiro
2. Verifique se o arquivo `.kiro/prompt-logs/<sua-branch>.md` foi criado
3. Abra o arquivo e confirme que o prompt foi registrado

---

## Uso

### Uso Automático

**Não há nada a fazer!** O sistema funciona automaticamente sempre que você envia um prompt ao Kiro.

### Estrutura dos Logs

Os logs são salvos em:

```
.kiro/prompt-logs/
├── main.md                    # Logs da branch main
├── develop.md                 # Logs da branch develop
├── feature-auth.md            # Logs de feature/auth
└── bugfix-crash-fix.md        # Logs de bugfix/crash-fix
```

**Convenção de nomes:**
- Branches com `/` são convertidas para `-`
- Exemplo: `feature/nova-funcionalidade` → `feature-nova-funcionalidade.md`

### Formato de Entrada

Cada entrada de log segue este formato:

```markdown
## Prompt: <título extraído do prompt>
- Responsável: João Silva
- Branch: feature/nova-funcionalidade
- Data/hora: 2026-04-30 14:35:22 (Brasília)

### Prompt original
```
Implemente autenticação JWT no backend
```

---
```

**Campos:**
- **Prompt:** Primeiras 50 caracteres do prompt (título)
- **Responsável:** Nome do usuário Git (`git config user.name`)
- **Branch:** Nome da branch Git atual
- **Data/hora:** Timestamp no horário de Brasília (UTC-3)
- **Prompt original:** Conteúdo completo do prompt

---

## Consultando Logs

### Ver Logs de uma Branch

Para visualizar todos os logs de uma branch específica:

```bash
cat .kiro/prompt-logs/<branch-name>.md
```

**Exemplo:**
```bash
cat .kiro/prompt-logs/feature-auth.md
```

### Ver Últimas Entradas

Para ver apenas as últimas entradas (últimas 50 linhas):

```bash
tail -n 50 .kiro/prompt-logs/<branch-name>.md
```

### Buscar por Palavra-chave

Para buscar prompts que contenham uma palavra-chave específica:

```bash
grep -A 10 "palavra-chave" .kiro/prompt-logs/<branch-name>.md
```

**Exemplo:** Buscar todos os prompts relacionados a "autenticação":
```bash
grep -A 10 "autenticação" .kiro/prompt-logs/feature-auth.md
```

### Ver Logs de Todas as Branches

Para listar todos os arquivos de log disponíveis:

```bash
ls -lh .kiro/prompt-logs/
```

### Buscar em Todos os Logs

Para buscar uma palavra-chave em todos os logs:

```bash
grep -r "palavra-chave" .kiro/prompt-logs/
```

---

## Casos de Uso

### 1. Code Review

**Cenário:** Você está revisando um Pull Request e quer entender o contexto das decisões tomadas.

**Solução:**
```bash
# Ver logs da branch do PR
cat .kiro/prompt-logs/feature-nova-funcionalidade.md
```

Isso permite entender:
- Quais prompts foram executados
- Quando foram executados
- Quem executou
- Contexto das mudanças

### 2. Documentação de Processo

**Cenário:** Você quer documentar como uma funcionalidade foi desenvolvida.

**Solução:** Os logs servem como documentação automática do processo de desenvolvimento, mostrando a evolução das ideias e decisões.

### 3. Auditoria de Mudanças

**Cenário:** Você precisa auditar quando e por que uma mudança foi feita.

**Solução:** Os logs fornecem rastreabilidade completa com timestamps e responsáveis.

### 4. Compartilhamento de Conhecimento

**Cenário:** Um novo membro da equipe quer entender como o projeto foi desenvolvido.

**Solução:** Os logs servem como histórico de aprendizado, mostrando as interações com o Kiro.

---

## Troubleshooting

### Problema: Logs não estão sendo criados

**Possíveis causas e soluções:**

1. **Hook não está ativo**
   ```bash
   # Verificar se o arquivo existe
   ls -la .kiro/hooks/prompt-logger.json
   ```
   - Se não existir, o hook não foi instalado corretamente

2. **Script não existe**
   ```bash
   # Verificar se o script existe
   ls -la .kiro/scripts/log_prompt.py
   ```
   - Se não existir, o script não foi instalado corretamente

3. **Dependência pytz não instalada**
   ```bash
   # Verificar se pytz está instalado
   python3 -c "import pytz; print('OK')"
   ```
   - Se retornar erro, instale: `pip install pytz`

4. **Permissões de execução**
   ```bash
   # Dar permissão de execução ao script
   chmod +x .kiro/scripts/log_prompt.py
   ```

5. **Kiro não carregou o hook**
   - Reinicie o Kiro para recarregar os hooks

### Problema: Conteúdo do prompt não é capturado

**Sintoma:** Logs contêm `[Conteúdo do prompt não capturado automaticamente]`

**Causa:** Esta é uma **limitação conhecida**. O Kiro pode não expor o conteúdo completo do prompt via hooks.

**Impacto:** Os metadados (branch, usuário, timestamp) ainda são registrados corretamente.

**Solução:** Não há solução no momento. Esta é uma limitação da API de hooks do Kiro. Os metadados ainda fornecem rastreabilidade valiosa.

### Problema: Erro ao executar o script

**Sintoma:** Mensagens de erro no terminal como `[Prompt Logger] Erro ao registrar prompt`

**Causa:** Pode ser um problema de permissões, Git não configurado, ou outro erro inesperado.

**Solução:**
1. Verificar se Git está instalado e configurado:
   ```bash
   git --version
   git config user.name
   ```

2. Verificar permissões do diretório `.kiro/prompt-logs/`:
   ```bash
   ls -ld .kiro/prompt-logs/
   ```

3. Executar o script manualmente para ver o erro completo:
   ```bash
   python3 .kiro/scripts/log_prompt.py
   ```

### Problema: Arquivo de log está muito grande

**Sintoma:** Arquivo `.md` com centenas de entradas, lento para abrir.

**Causa:** Logs crescem indefinidamente com o uso.

**Solução temporária:**
1. Arquivar logs antigos manualmente:
   ```bash
   # Criar backup
   mv .kiro/prompt-logs/feature-antiga.md .kiro/prompt-logs/archive/feature-antiga-2026-04.md
   ```

2. Ou visualizar apenas as últimas entradas:
   ```bash
   tail -n 100 .kiro/prompt-logs/feature-antiga.md
   ```

**Solução futura:** Rotação automática de logs está planejada para uma versão futura.

### Problema: Conflitos de merge em logs

**Sintoma:** Git reporta conflito em arquivo `.kiro/prompt-logs/<branch>.md`

**Causa:** Duas pessoas trabalharam na mesma branch simultaneamente.

**Solução:**
1. Abrir o arquivo com conflito
2. Aceitar ambas as mudanças (ambas as entradas de log são válidas)
3. Remover marcadores de conflito do Git (`<<<<<<<`, `=======`, `>>>>>>>`)
4. Salvar e fazer commit

**Dica:** O formato incremental facilita a resolução - geralmente basta manter ambas as seções.

---

## Limitações Conhecidas

### 1. Captura de Conteúdo do Prompt

**Limitação:** O Kiro pode não expor o conteúdo completo do prompt via hooks.

**Impacto:**
- Logs podem conter apenas metadados (branch, usuário, timestamp)
- Placeholder `[Conteúdo do prompt não capturado automaticamente]` é usado

**Status:** Limitação da API de hooks do Kiro. Metadados ainda fornecem rastreabilidade.

### 2. Resumo de Resultados

**Limitação:** O sistema não captura o resumo do resultado gerado pelo Kiro.

**Impacto:** Logs contêm apenas o prompt de entrada, não a resposta do agente.

**Status:** Planejado para fase futura (requer hook `agentStop`).

### 3. Crescimento Indefinido de Arquivos

**Limitação:** Arquivos de log crescem indefinidamente com append.

**Impacto:** Arquivos muito grandes podem ser lentos para abrir/editar.

**Mitigação:**
- Formato incremental facilita leitura das últimas entradas
- Arquivamento manual quando necessário

**Status:** Rotação automática planejada para fase futura.

### 4. Timezone Fixo (Brasília)

**Limitação:** Todos os timestamps usam horário de Brasília (America/Sao_Paulo).

**Impacto:** Equipes em outros fusos horários verão timestamps em horário de Brasília.

**Justificativa:** Requisito do projeto para consistência em equipes distribuídas.

---

## Boas Práticas

### 1. Revisar Logs Antes de Commits

Antes de fazer commit, revise os logs para garantir que não contêm informações sensíveis:

```bash
git diff .kiro/prompt-logs/
```

### 2. Não Incluir Dados Sensíveis em Prompts

Evite incluir em prompts:
- ❌ Tokens de API
- ❌ Senhas
- ❌ Chaves privadas
- ❌ Dados pessoais sensíveis

### 3. Usar Logs em Code Reviews

Ao revisar PRs, consulte os logs da branch para entender o contexto:

```bash
cat .kiro/prompt-logs/<branch-do-pr>.md
```

### 4. Arquivar Logs de Branches Antigas

Quando uma branch é mergeada e deletada, considere arquivar seus logs:

```bash
mkdir -p .kiro/prompt-logs/archive
mv .kiro/prompt-logs/feature-antiga.md .kiro/prompt-logs/archive/
```

### 5. Consultar Logs para Aprendizado

Use logs de branches bem-sucedidas como referência para novos desenvolvimentos.

---

## Configuração Avançada

### Desabilitar Logging (se necessário)

Se você precisar desabilitar temporariamente o logging:

1. **Opção 1:** Renomear o hook
   ```bash
   mv .kiro/hooks/prompt-logger.json .kiro/hooks/prompt-logger.json.disabled
   ```

2. **Opção 2:** Deletar o hook
   ```bash
   rm .kiro/hooks/prompt-logger.json
   ```

Para reabilitar, reverta a operação.

### Não Versionar Logs no Git

Se você preferir não versionar os logs no Git, adicione ao `.gitignore`:

```gitignore
# Prompt logs
.kiro/prompt-logs/
```

**Nota:** Por padrão, logs são versionados para rastreabilidade em code reviews.

### Customizar Timeout do Hook

O hook tem timeout de 5 segundos. Para alterar, edite `.kiro/hooks/prompt-logger.json`:

```json
{
  "timeout": 10
}
```

---

## Perguntas Frequentes (FAQ)

### O logging afeta a performance do Kiro?

**Não.** O script é executado de forma assíncrona e tem overhead mínimo (<100ms). Você não notará diferença na velocidade de execução.

### Os logs ocupam muito espaço em disco?

**Não.** Arquivos Markdown são muito leves. Mesmo com centenas de entradas, um arquivo de log raramente ultrapassa alguns MB.

### Posso deletar logs antigos?

**Sim.** Você pode deletar ou arquivar logs de branches antigas sem problemas. Isso não afeta o funcionamento do sistema.

### Os logs são privados?

**Depende.** Se o repositório é privado, os logs também são. Se o repositório é público, os logs serão públicos. Revise antes de fazer push.

### Posso usar em outros projetos?

**Sim!** O sistema é genérico e pode ser usado em qualquer projeto que utilize o Kiro. Basta copiar:
- `.kiro/hooks/prompt-logger.json`
- `.kiro/scripts/log_prompt.py`
- Instalar `pytz`

### O que acontece se o Git não estiver configurado?

O script usa fallbacks:
- Branch: `unknown-branch`
- Usuário: `Unknown User`
- Timestamp: UTC (se pytz não estiver disponível)

O sistema continua funcionando, mas com metadados limitados.

---

## Evolução Futura

### Fase 2: Captura de Resultados

**Planejado:**
- Hook `agentStop` para capturar fim da execução
- Resumo automático da resposta do agente
- Associação prompt → resultado no log

**Formato esperado:**
```markdown
## Prompt: Implementar autenticação JWT
...

### Resultado
- Status: Sucesso
- Arquivos modificados: 3
- Testes executados: 5 (todos passaram)
- Resumo: Implementada autenticação JWT com testes unitários
```

### Fase 3: Interface de Consulta

**Planejado:**
- CLI para buscar logs: `kiro-logs search "keyword"`
- Filtros por data, branch, usuário
- Exportação para JSON/CSV
- Estatísticas de uso

**Exemplo:**
```bash
kiro-logs search "autenticação" --branch feature/auth --after 2026-04-01
```

### Fase 4: Rotação e Arquivamento

**Planejado:**
- Arquivamento automático de logs antigos
- Compressão de arquivos grandes
- Política de retenção configurável

**Exemplo de configuração:**
```json
{
  "retention": {
    "maxEntriesPerFile": 100,
    "archiveAfterDays": 90,
    "compressArchives": true
  }
}
```

---

## Suporte

### Reportar Problemas

Se você encontrar problemas com o sistema de logging:

1. Verifique a seção [Troubleshooting](#troubleshooting)
2. Execute o script manualmente para ver erros: `python3 .kiro/scripts/log_prompt.py`
3. Abra uma issue no repositório com:
   - Descrição do problema
   - Mensagens de erro (se houver)
   - Versão do Python: `python3 --version`
   - Versão do Git: `git --version`

### Contribuir

Contribuições são bem-vindas! Áreas de interesse:

- Melhorias na captura de conteúdo do prompt
- Interface de consulta de logs
- Rotação automática de logs
- Integração com outras ferramentas

---

## Referências

- **Spec completa:** `.kiro/specs/prompt-logging/`
- **Design técnico:** `.kiro/specs/prompt-logging/design.md`
- **Requisitos:** `.kiro/specs/prompt-logging/requirements.md`
- **Steering file:** `.kiro/steering/prompt-logging.md`
- **Git Flow do projeto:** `.kiro/steering/gitflow.md`

---

## Resumo Rápido

| Aspecto | Detalhes |
|---------|----------|
| **O que faz** | Registra automaticamente prompts do Kiro por branch |
| **Onde salva** | `.kiro/prompt-logs/<branch-name>.md` |
| **Formato** | Markdown estruturado |
| **Ação necessária** | Nenhuma (automático) |
| **Dependências** | Python 3.8+, pytz, Git |
| **Performance** | <100ms overhead |
| **Limitações** | Pode não capturar conteúdo do prompt |

---

**Versão:** 1.0.0  
**Última atualização:** 2026-04-30  
**Autor:** Sistema de Prompt Logging
