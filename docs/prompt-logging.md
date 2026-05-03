# Prompt Logging — FundamentAI

Sistema automático de registro de prompts executados no Kiro, organizado por branch Git.

---

## Visão Geral

Cada prompt enviado ao Kiro é registrado automaticamente em um arquivo Markdown dentro de `.kiro/prompt-logs/`, usando o nome da branch ativa como nome do arquivo.

```
Kiro (promptSubmit) → Hook → Script Python → .kiro/prompt-logs/<branch>.md
```

---

## Instalação

### 1. Instalar dependência Python

```bash
pip install pytz
```

> Sem `pytz`, o script usa UTC como fallback e exibe um aviso no stderr.

### 2. Verificar arquivos

```
.kiro/
├── hooks/
│   └── prompt-logger.json    ← hook do Kiro
└── scripts/
    └── log_prompt.py         ← script de logging
```

### 3. Reiniciar o Kiro

Após adicionar o hook, reinicie o Kiro para que ele seja carregado.

---

## Uso

**Automático.** Nenhuma ação manual é necessária. Cada prompt enviado ao Kiro gera uma entrada no arquivo de log da branch ativa.

---

## Estrutura dos Logs

Cada branch tem seu próprio arquivo:

```
.kiro/prompt-logs/
├── main.md
├── develop.md
├── feature-coletor-yfinance.md
└── bugfix-calculo-roe.md
```

### Formato de cada entrada

```markdown
## Prompt: <título extraído do prompt>
- Responsável: <nome do usuário Git>
- Branch: <nome-da-branch>
- Data/hora: YYYY-MM-DD HH:MM:SS (Brasília)

### Prompt original
```
<conteúdo completo do prompt>
```

---
```

---

## Consulta de Logs

**Ver log completo de uma branch:**
```bash
cat .kiro/prompt-logs/feature-coletor-yfinance.md
```

**Últimas entradas:**
```bash
tail -n 50 .kiro/prompt-logs/feature-coletor-yfinance.md
```

**Buscar por palavra-chave:**
```bash
grep -A 10 "endpoint" .kiro/prompt-logs/develop.md
```

---

## Limitações Conhecidas

### Captura de conteúdo do prompt

O Kiro pode não expor o conteúdo completo do prompt via hooks. Nesse caso:
- O log registra o placeholder: `[Conteúdo do prompt não capturado automaticamente]`
- Metadados (branch, usuário, timestamp) são sempre registrados

### Resumo de resultados

O MVP não captura a resposta do agente. Planejado para fase futura via hook `agentStop`.

---

## Convenções

| Situação | Comportamento |
|---|---|
| Branch `feature/auth` | Arquivo `feature-auth.md` (barras → hífens) |
| Sem Git configurado | Usa `unknown-branch` e `Unknown User` |
| Sem `pytz` instalado | Usa UTC com aviso no stderr |
| Erro no script | Registra em stderr, não bloqueia o Kiro |

---

## Troubleshooting

**Logs não estão sendo criados:**
1. Verificar se o hook existe: `.kiro/hooks/prompt-logger.json`
2. Verificar se o script existe: `.kiro/scripts/log_prompt.py`
3. Reiniciar o Kiro para recarregar os hooks
4. Executar o script manualmente para testar: `python .kiro/scripts/log_prompt.py`

**Timestamp em UTC em vez de Brasília:**
```bash
pip install pytz
```

---

## Referências

- Spec completa: `.kiro/specs/prompt-logging/`
- Steering file: `.kiro/steering/prompt-logging.md`
- Git Flow do projeto: `.kiro/steering/gitflow.md`
