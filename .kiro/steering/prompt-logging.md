# Prompt Logging

## Visão Geral

Este projeto implementa um sistema automático de logging de prompts executados no Kiro, organizado por branch Git. O objetivo é manter rastreabilidade completa das interações com o agente durante o desenvolvimento.

---

## Arquitetura

```
Kiro (promptSubmit) → Hook → Script Python → Arquivo .md por branch
```

### Componentes

1. **Hook:** `.kiro/hooks/prompt-logger.json` - Intercepta evento `promptSubmit`
2. **Script:** `.kiro/scripts/log_prompt.py` - Coleta metadados e persiste logs
3. **Logs:** `.kiro/prompt-logs/<branch-name>.md` - Arquivos de log por branch

---

## Estrutura de Logs

Cada branch tem seu próprio arquivo de log:

```
.kiro/prompt-logs/
├── main.md
├── develop.md
├── feature-auth.md
└── bugfix-crash-fix.md
```

### Formato de Entrada

```markdown
## Prompt: <título extraído do prompt>
- Responsável: <nome do usuário Git>
- Branch: <nome-da-branch>
- Data/hora: <YYYY-MM-DD HH:mm:SS> (Brasília)

### Prompt original
```
<conteúdo completo do prompt>
```

---
```

---

## Uso

### Automático

Nenhuma ação manual é necessária. Prompts são registrados automaticamente quando submetidos ao Kiro.

### Consulta de Logs

**Ver logs de uma branch:**
```bash
cat .kiro/prompt-logs/<branch-name>.md
```

**Últimas entradas:**
```bash
tail -n 50 .kiro/prompt-logs/<branch-name>.md
```

**Buscar por palavra-chave:**
```bash
grep -A 10 "palavra-chave" .kiro/prompt-logs/<branch-name>.md
```

---

## Convenções

### Nomes de Arquivo

- Branches com `/` são convertidas para `-`
- Exemplo: `feature/auth` → `feature-auth.md`

### Timezone

- Todos os timestamps usam horário de Brasília (America/Sao_Paulo)
- Formato: `YYYY-MM-DD HH:MM:SS`

### Versionamento

- Logs são versionados no Git por padrão
- Facilita rastreabilidade em code reviews
- Preserva histórico de decisões

---

## Limitações Conhecidas

### 1. Captura de Conteúdo do Prompt

O Kiro pode não expor o conteúdo completo do prompt via hooks. Neste caso:
- Logs conterão placeholder: `[Conteúdo não capturado]`
- Metadados (branch, usuário, timestamp) ainda são registrados

### 2. Resumo de Resultados

MVP não inclui captura de resultados do agente. Planejado para fase futura.

### 3. Crescimento de Arquivos

Arquivos de log crescem indefinidamente. Estratégia de rotação planejada para fase futura.

---

## Manutenção

### Dependências

- Python 3.8+
- `pytz` (timezone de Brasília)

**Instalação:**
```bash
pip install pytz
```

### Troubleshooting

**Logs não estão sendo criados:**
1. Verificar se hook existe: `.kiro/hooks/prompt-logger.json`
2. Verificar se script existe: `.kiro/scripts/log_prompt.py`
3. Verificar permissões de execução do script
4. Verificar logs de erro do Kiro

**Conteúdo não é capturado:**
- Limitação conhecida do Kiro
- Metadados ainda são registrados
- Considerar captura manual se necessário

---

## Contexto para o Agente Kiro

Quando trabalhar com prompt logging:

1. **Não modificar formato de log** - Manter consistência para parsing futuro
2. **Tratar erros graciosamente** - Nunca bloquear execução do Kiro
3. **Preservar histórico** - Sempre usar append, nunca sobrescrever
4. **Sanitizar nomes** - Converter caracteres especiais em nomes de arquivo válidos
5. **Documentar limitações** - Ser transparente sobre o que não é capturado

---

## Evolução Futura

### Fase 2: Captura de Resultados
- Hook `agentStop` para capturar fim da execução
- Resumo automático da resposta do agente
- Associação prompt → resultado

### Fase 3: Interface de Consulta
- CLI para buscar logs
- Filtros por data, branch, usuário
- Exportação para outros formatos

### Fase 4: Rotação e Arquivamento
- Arquivamento automático de logs antigos
- Compressão de arquivos grandes
- Política de retenção configurável

---

## Referências

- Spec completa: `.kiro/specs/prompt-logging/`
- Documentação de uso: `docs/prompt-logging.md`
- Git Flow do projeto: `.kiro/steering/gitflow.md`
