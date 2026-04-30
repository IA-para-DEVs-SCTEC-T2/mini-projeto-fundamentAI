# Design Técnico: Prompt Logging

## Visão Geral da Arquitetura

Sistema de logging baseado em hooks do Kiro que captura eventos `promptSubmit` e executa um script Python para registrar prompts em arquivos Markdown organizados por branch Git.

```
┌─────────────────┐
│  Usuário Kiro   │
└────────┬────────┘
         │ prompt
         ▼
┌─────────────────┐
│   Kiro Agent    │
└────────┬────────┘
         │ evento: promptSubmit
         ▼
┌─────────────────┐
│  Hook Handler   │ (.kiro/hooks/prompt-logger.json)
└────────┬────────┘
         │ executa
         ▼
┌─────────────────┐
│  Script Python  │ (.kiro/scripts/log_prompt.py)
└────────┬────────┘
         │
         ├─> git rev-parse --abbrev-ref HEAD
         ├─> git config user.name
         ├─> pytz (timezone Brasília)
         │
         ▼
┌─────────────────┐
│  Arquivo de Log │ (.kiro/prompt-logs/<branch>.md)
└─────────────────┘
```

---

## Componentes

### 1. Hook do Kiro

**Arquivo:** `.kiro/hooks/prompt-logger.json`

**Responsabilidade:** Interceptar evento `promptSubmit` e acionar o script de logging.

**Estrutura:**
```json
{
  "name": "Prompt Logger",
  "version": "1.0.0",
  "description": "Registra automaticamente prompts executados no Kiro, organizados por branch Git",
  "when": {
    "type": "promptSubmit"
  },
  "then": {
    "type": "runCommand",
    "command": "python3 .kiro/scripts/log_prompt.py"
  }
}
```

**Decisões de Design:**
- Usa `runCommand` em vez de `askAgent` para evitar overhead de invocação do agente
- Executa de forma assíncrona para não bloquear o fluxo do usuário
- Não especifica `patterns` ou `toolTypes` pois deve capturar todos os prompts

---

### 2. Script de Logging

**Arquivo:** `.kiro/scripts/log_prompt.py`

**Responsabilidade:** Coletar metadados, formatar entrada de log e persistir no arquivo correto.

**Fluxo de Execução:**

```python
1. Detectar branch Git atual
   └─> git rev-parse --abbrev-ref HEAD

2. Obter nome do usuário Git
   └─> git config user.name

3. Gerar timestamp em horário de Brasília
   └─> datetime.now(pytz.timezone('America/Sao_Paulo'))

4. Tentar capturar conteúdo do prompt
   └─> Verificar variáveis de ambiente ou stdin
   └─> Se não disponível: registrar "[Conteúdo não capturado]"

5. Determinar caminho do arquivo de log
   └─> .kiro/prompt-logs/<branch-name>.md

6. Criar diretório se não existir
   └─> os.makedirs('.kiro/prompt-logs', exist_ok=True)

7. Formatar entrada de log
   └─> Template Markdown estruturado

8. Adicionar ao arquivo (append mode)
   └─> with open(log_file, 'a', encoding='utf-8') as f

9. Tratar erros graciosamente
   └─> Log de erro em stderr, mas não falha
```

**Estrutura do Código:**

```python
#!/usr/bin/env python3
"""
Script de logging de prompts do Kiro.
Captura metadados e registra prompts em arquivos organizados por branch.
"""

import os
import sys
import subprocess
from datetime import datetime
import pytz

def get_git_branch():
    """Retorna a branch Git atual."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return 'unknown-branch'

def get_git_user():
    """Retorna o nome do usuário Git."""
    try:
        result = subprocess.run(
            ['git', 'config', 'user.name'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return 'Unknown User'

def get_brasilia_timestamp():
    """Retorna timestamp formatado no horário de Brasília."""
    tz = pytz.timezone('America/Sao_Paulo')
    now = datetime.now(tz)
    return now.strftime('%Y-%m-%d %H:%M:%S')

def get_prompt_content():
    """
    Tenta capturar o conteúdo do prompt.
    
    Estratégias:
    1. Variável de ambiente KIRO_PROMPT (se disponível)
    2. Stdin (se disponível)
    3. Placeholder se não disponível
    """
    # Estratégia 1: Variável de ambiente
    prompt = os.environ.get('KIRO_PROMPT')
    if prompt:
        return prompt
    
    # Estratégia 2: Stdin (se não for TTY)
    if not sys.stdin.isatty():
        try:
            prompt = sys.stdin.read().strip()
            if prompt:
                return prompt
        except Exception:
            pass
    
    # Estratégia 3: Placeholder
    return "[Conteúdo do prompt não capturado automaticamente]"

def sanitize_branch_name(branch):
    """Sanitiza nome da branch para uso em nome de arquivo."""
    # Remove caracteres problemáticos
    return branch.replace('/', '-').replace('\\', '-')

def format_log_entry(branch, user, timestamp, prompt_content):
    """Formata entrada de log no padrão Markdown."""
    # Gera título baseado nas primeiras palavras do prompt
    title = prompt_content[:50] + '...' if len(prompt_content) > 50 else prompt_content
    title = title.replace('\n', ' ').strip()
    
    if title == "[Conteúdo do prompt não capturado automaticamente]":
        title = "Prompt não capturado"
    
    entry = f"""## Prompt: {title}
- Responsável: {user}
- Branch: {branch}
- Data/hora: {timestamp} (Brasília)

### Prompt original
```
{prompt_content}
```

---

"""
    return entry

def log_prompt():
    """Função principal de logging."""
    try:
        # Coleta metadados
        branch = get_git_branch()
        user = get_git_user()
        timestamp = get_brasilia_timestamp()
        prompt_content = get_prompt_content()
        
        # Prepara arquivo de log
        sanitized_branch = sanitize_branch_name(branch)
        log_dir = '.kiro/prompt-logs'
        log_file = os.path.join(log_dir, f'{sanitized_branch}.md')
        
        # Cria diretório se não existir
        os.makedirs(log_dir, exist_ok=True)
        
        # Adiciona cabeçalho se arquivo não existir
        if not os.path.exists(log_file):
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f'# Prompt Logs: {branch}\n\n')
                f.write('Histórico de prompts executados no Kiro nesta branch.\n\n')
                f.write('---\n\n')
        
        # Formata e adiciona entrada
        entry = format_log_entry(branch, user, timestamp, prompt_content)
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(entry)
        
        # Sucesso silencioso (não imprime nada para não poluir output)
        
    except Exception as e:
        # Log de erro em stderr, mas não falha
        print(f"[Prompt Logger] Erro ao registrar prompt: {e}", file=sys.stderr)
        # Não levanta exceção para não bloquear o Kiro

if __name__ == '__main__':
    log_prompt()
```

**Decisões de Design:**

1. **Tratamento de Erros Gracioso:** Nunca falha de forma que bloqueie o Kiro
2. **Sanitização de Nomes:** Converte `/` em `-` para nomes de arquivo válidos
3. **Encoding UTF-8:** Suporta caracteres especiais em prompts
4. **Append Mode:** Preserva histórico existente
5. **Cabeçalho Automático:** Adiciona cabeçalho na primeira entrada de cada branch
6. **Fallback para Conteúdo:** Se não conseguir capturar, registra placeholder

---

### 3. Estrutura de Arquivos de Log

**Localização:** `.kiro/prompt-logs/<branch-name>.md`

**Formato:**

```markdown
# Prompt Logs: <branch-name>

Histórico de prompts executados no Kiro nesta branch.

---

## Prompt: <título extraído do prompt>
- Responsável: <nome do usuário Git>
- Branch: <nome-da-branch>
- Data/hora: <YYYY-MM-DD HH:mm:ss> (Brasília)

### Prompt original
```
<conteúdo completo do prompt>
```

---

## Prompt: <próximo prompt>
...
```

**Características:**
- Formato Markdown para legibilidade
- Separadores visuais (`---`) entre entradas
- Blocos de código para preservar formatação do prompt
- Metadados estruturados para fácil parsing futuro

---

## Fluxo de Dados

### Captura de Prompt

```
Usuário → Kiro → promptSubmit event → Hook → Script Python
                                                    │
                                                    ├─> Git (branch, user)
                                                    ├─> Sistema (timestamp)
                                                    ├─> Env/Stdin (prompt)
                                                    │
                                                    ▼
                                              Arquivo .md
```

### Organização de Arquivos

```
.kiro/
├── hooks/
│   └── prompt-logger.json          # Hook de captura
├── scripts/
│   └── log_prompt.py               # Script de logging
├── prompt-logs/
│   ├── main.md                     # Logs da branch main
│   ├── develop.md                  # Logs da branch develop
│   ├── feature-auth.md             # Logs de feature/auth
│   └── bugfix-crash-fix.md         # Logs de bugfix/crash-fix
└── steering/
    └── prompt-logging.md           # Documentação de uso
```

---

## Decisões Técnicas

### Linguagem: Python

**Justificativa:**
- Já é a linguagem principal do projeto (backend)
- Biblioteca `pytz` para timezone de Brasília
- Fácil integração com Git via subprocess
- Tratamento robusto de arquivos e encoding

### Formato: Markdown

**Justificativa:**
- Legível em texto puro
- Renderizado automaticamente no GitHub/GitLab
- Fácil de fazer diff no Git
- Estruturado mas flexível

### Organização: Um arquivo por branch

**Justificativa:**
- Isolamento natural entre branches
- Facilita consulta de logs de uma branch específica
- Evita conflitos de merge (cada branch tem seu arquivo)
- Alinhado com o Git Flow do projeto

**Alternativa Rejeitada:** Diretório por branch (`.kiro/prompt-logs/<branch>/prompts.md`)
- Mais complexo
- Mais arquivos para gerenciar
- Sem benefício claro

### Timezone: Brasília (America/Sao_Paulo)

**Justificativa:**
- Requisito explícito do usuário
- Consistência em equipes distribuídas
- Usa `pytz` para precisão (considera horário de verão)

---

## Limitações Conhecidas

### 1. Captura de Conteúdo do Prompt

**Limitação:** O Kiro pode não expor o conteúdo do prompt via variáveis de ambiente ou stdin no contexto do hook.

**Impacto:** Logs podem conter apenas metadados (branch, usuário, timestamp) sem o conteúdo real do prompt.

**Mitigação:**
- Script tenta múltiplas estratégias de captura
- Registra placeholder se não conseguir capturar
- Documenta limitação claramente

**Validação Necessária:** Testar em ambiente real para confirmar se captura funciona.

### 2. Resumo de Resultados

**Limitação:** Capturar o "resumo do resultado gerado pelo Kiro" requer hook `agentStop` e acesso à resposta do agente.

**Impacto:** MVP não inclui resumo de resultados.

**Mitigação:** Documentar como evolução futura (Fase 2).

### 3. Performance em Branches com Muitos Logs

**Limitação:** Arquivos de log crescem indefinidamente com append.

**Impacto:** Arquivos muito grandes podem ser lentos para abrir/editar.

**Mitigação:**
- Formato incremental facilita leitura das últimas entradas
- Documentar estratégia de rotação para fase futura
- Considerar limite de tamanho ou arquivamento automático

### 4. Conflitos de Merge

**Limitação:** Se duas pessoas trabalharem na mesma branch simultaneamente, pode haver conflitos no arquivo de log.

**Impacto:** Baixo - formato incremental facilita resolução manual.

**Mitigação:** Documentar como resolver conflitos (geralmente aceitar ambas as mudanças).

---

## Dependências

### Dependências de Sistema
- Git 2.0+
- Python 3.8+

### Dependências Python
- `pytz` (timezone de Brasília)

**Instalação:**
```bash
pip install pytz
```

ou adicionar a `requirements.txt`:
```
pytz>=2024.1
```

---

## Testes

### Casos de Teste

#### TC01: Primeiro Prompt em Nova Branch
**Pré-condição:** Branch `feature/test` sem arquivo de log existente

**Passos:**
1. Checkout para `feature/test`
2. Executar prompt no Kiro
3. Verificar criação de `.kiro/prompt-logs/feature-test.md`
4. Verificar presença de cabeçalho e primeira entrada

**Resultado Esperado:** Arquivo criado com cabeçalho e entrada formatada corretamente.

#### TC02: Múltiplos Prompts na Mesma Branch
**Pré-condição:** Branch com arquivo de log existente

**Passos:**
1. Executar 3 prompts consecutivos
2. Verificar arquivo de log

**Resultado Esperado:** 3 entradas adicionadas, ordem cronológica preservada, sem sobrescrita.

#### TC03: Troca de Branch
**Pré-condição:** Duas branches diferentes

**Passos:**
1. Executar prompt na `branch-a`
2. Checkout para `branch-b`
3. Executar prompt na `branch-b`
4. Verificar ambos os arquivos de log

**Resultado Esperado:** Dois arquivos distintos, cada um com logs da respectiva branch.

#### TC04: Branch com Caracteres Especiais
**Pré-condição:** Branch `feature/auth/jwt-impl`

**Passos:**
1. Executar prompt
2. Verificar nome do arquivo criado

**Resultado Esperado:** Arquivo `.kiro/prompt-logs/feature-auth-jwt-impl.md` criado (barras convertidas em hífens).

#### TC05: Erro de Git (não em repositório)
**Pré-condição:** Executar fora de repositório Git

**Passos:**
1. Executar script manualmente fora de repo Git
2. Verificar comportamento

**Resultado Esperado:** Script não falha, usa `unknown-branch` e `Unknown User`.

---

## Segurança e Privacidade

### Dados Registrados
- ✅ Branch Git (não sensível)
- ✅ Nome do usuário Git (não sensível)
- ✅ Timestamp (não sensível)
- ✅ Conteúdo do prompt (pode conter informações do projeto)

### Dados NÃO Registrados
- ❌ Tokens de API
- ❌ Senhas
- ❌ Chaves privadas
- ❌ Variáveis de ambiente sensíveis

### Recomendações
- Revisar logs antes de commits em repositórios públicos
- Adicionar `.kiro/prompt-logs/` ao `.gitignore` se necessário (decisão do projeto)
- Não incluir dados sensíveis em prompts

---

## Configuração do .gitignore

**Decisão:** Por padrão, logs são versionados no Git para rastreabilidade.

**Alternativa:** Se o projeto preferir não versionar logs:

```gitignore
# Prompt logs (opcional)
.kiro/prompt-logs/
```

**Recomendação:** Versionar logs para:
- Rastreabilidade em code reviews
- Documentação do processo de desenvolvimento
- Compartilhamento de conhecimento

---

## Documentação de Uso

### Instalação

1. **Instalar dependências:**
   ```bash
   pip install pytz
   ```

2. **Verificar estrutura:**
   ```
   .kiro/
   ├── hooks/prompt-logger.json
   └── scripts/log_prompt.py
   ```

3. **Tornar script executável (opcional):**
   ```bash
   chmod +x .kiro/scripts/log_prompt.py
   ```

4. **Reiniciar Kiro** para carregar o hook (se necessário).

### Uso

**Automático:** Nenhuma ação necessária. Prompts são registrados automaticamente.

### Consulta de Logs

**Por branch:**
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

### Troubleshooting

**Logs não estão sendo criados:**
1. Verificar se hook está ativo: `.kiro/hooks/prompt-logger.json`
2. Verificar se script existe: `.kiro/scripts/log_prompt.py`
3. Verificar permissões de execução
4. Verificar logs de erro do Kiro

**Conteúdo do prompt não é capturado:**
- Limitação conhecida: Kiro pode não expor conteúdo via hook
- Logs conterão placeholder: "[Conteúdo não capturado]"
- Metadados (branch, usuário, timestamp) ainda são registrados

---

## Evolução Futura (Fase 2)

### Captura de Resultados
- Hook `agentStop` para capturar fim da execução
- Resumo automático da resposta do agente
- Associação prompt → resultado

### Interface de Consulta
- CLI para buscar logs: `kiro-logs search "keyword"`
- Filtros por data, branch, usuário
- Exportação para outros formatos (JSON, CSV)

### Rotação de Logs
- Arquivamento automático de logs antigos
- Compressão de arquivos grandes
- Política de retenção configurável

### Integração com Ferramentas
- Integração com Jira/Linear (associar prompts a issues)
- Métricas de uso do Kiro por branch/desenvolvedor
- Dashboard de análise de prompts

---

## Referências

- [Kiro Hooks Documentation](https://kiro.dev/docs/hooks)
- [Python subprocess](https://docs.python.org/3/library/subprocess.html)
- [pytz Documentation](https://pythonhosted.org/pytz/)
- Git Flow do projeto: `.kiro/steering/gitflow.md`
