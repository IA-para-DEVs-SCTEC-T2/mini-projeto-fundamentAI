# Funções de Coleta de Metadados - Documentação

## Visão Geral

Este documento descreve as três funções implementadas para coleta de metadados no sistema de Prompt Logging. Todas as funções foram projetadas com tratamento gracioso de erros, garantindo que falhas não bloqueiem a execução do sistema.

---

## Funções Implementadas

### 1. `get_git_branch()`

**Propósito:** Detecta a branch Git atual do repositório.

**Retorno:**
- `str`: Nome da branch atual (ex: `'main'`, `'feature/auth'`)
- `'unknown-branch'`: Valor de fallback em caso de erro

**Tratamento de Erros:**

| Erro | Causa | Fallback |
|------|-------|----------|
| `FileNotFoundError` | Git não está instalado | `'unknown-branch'` |
| `CalledProcessError` | Não é um repositório Git | `'unknown-branch'` |
| `TimeoutExpired` | Comando Git demorou >5s | `'unknown-branch'` |
| `Exception` | Qualquer outro erro | `'unknown-branch'` |
| Retorno vazio | Branch sem nome | `'unknown-branch'` |

**Implementação:**
```python
subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], ...)
```

**Timeout:** 5 segundos para evitar travamentos.

---

### 2. `get_git_user()`

**Propósito:** Obtém o nome do usuário Git configurado no repositório.

**Retorno:**
- `str`: Nome do usuário (ex: `'João Silva'`)
- `'Unknown User'`: Valor de fallback em caso de erro

**Tratamento de Erros:**

| Erro | Causa | Fallback |
|------|-------|----------|
| `FileNotFoundError` | Git não está instalado | `'Unknown User'` |
| `CalledProcessError` | `user.name` não configurado | `'Unknown User'` |
| `TimeoutExpired` | Comando Git demorou >5s | `'Unknown User'` |
| `Exception` | Qualquer outro erro | `'Unknown User'` |
| Retorno vazio | Nome vazio | `'Unknown User'` |

**Implementação:**
```python
subprocess.run(['git', 'config', 'user.name'], ...)
```

**Timeout:** 5 segundos para evitar travamentos.

---

### 3. `get_brasilia_timestamp()`

**Propósito:** Gera timestamp no horário de Brasília (America/Sao_Paulo).

**Retorno:**
- `str`: Timestamp no formato `'YYYY-MM-DD HH:MM:SS'` (ex: `'2026-04-30 15:30:45'`)
- `str`: Timestamp UTC com sufixo `'(UTC)'` em caso de erro (ex: `'2026-04-30 18:30:45 (UTC)'`)

**Tratamento de Erros:**

| Erro | Causa | Fallback |
|------|-------|----------|
| `Exception` | pytz não disponível ou erro no timezone | Timestamp UTC com sufixo `'(UTC)'` |

**Implementação:**
```python
tz = pytz.timezone('America/Sao_Paulo')
now = datetime.now(tz)
return now.strftime('%Y-%m-%d %H:%M:%S')
```

**Nota:** O timezone `America/Sao_Paulo` considera automaticamente horário de verão quando aplicável.

---

## Testes Implementados

### Testes Funcionais (`test_metadata_functions.py`)

Verifica que as funções retornam valores corretos em condições normais:

```bash
python3 .kiro/scripts/test_metadata_functions.py
```

**Saída esperada:**
```
============================================================
Testando funções de coleta de metadados
============================================================

1. Testando get_git_branch():
   ✓ Branch detectada: 'chore/definicao-gitflow'

2. Testando get_git_user():
   ✓ Usuário detectado: 'Alysson Girotto'

3. Testando get_brasilia_timestamp():
   ✓ Timestamp gerado: '2026-04-30 15:07:36'

✓ Todos os testes concluídos com sucesso!
```

### Testes de Tratamento de Erros (`test_error_handling.py`)

Verifica que as funções tratam erros graciosamente com fallbacks apropriados:

```bash
python3 .kiro/scripts/test_error_handling.py
```

**Cobertura de testes:**
- ✓ Git não instalado (`FileNotFoundError`)
- ✓ Não é repositório Git (`CalledProcessError`)
- ✓ Timeout de comandos Git (`TimeoutExpired`)
- ✓ Exceções genéricas
- ✓ Retornos vazios
- ✓ Erro no pytz (fallback para UTC)

---

## Dependências

### Bibliotecas Python

| Biblioteca | Versão | Propósito |
|------------|--------|-----------|
| `subprocess` | stdlib | Executar comandos Git |
| `datetime` | stdlib | Manipulação de timestamps |
| `pytz` | >=2024.1 | Timezone de Brasília |

### Dependências de Sistema

- **Git 2.0+**: Para detecção de branch e usuário
- **Python 3.8+**: Compatibilidade com f-strings e type hints

---

## Uso

### Importação

```python
from log_prompt import get_git_branch, get_git_user, get_brasilia_timestamp
```

### Exemplo de Uso

```python
# Coletar metadados
branch = get_git_branch()
user = get_git_user()
timestamp = get_brasilia_timestamp()

print(f"Branch: {branch}")
print(f"Usuário: {user}")
print(f"Timestamp: {timestamp}")
```

**Saída:**
```
Branch: feature/nova-funcionalidade
Usuário: João Silva
Timestamp: 2026-04-30 15:30:45
```

---

## Garantias de Confiabilidade

### 1. Nunca Falha

Todas as funções retornam valores de fallback em caso de erro. Nenhuma exceção é propagada para o código chamador.

### 2. Timeout Configurado

Comandos Git têm timeout de 5 segundos para evitar travamentos em sistemas lentos ou com problemas de rede.

### 3. Fallbacks Informativos

- `'unknown-branch'`: Indica claramente que a branch não foi detectada
- `'Unknown User'`: Indica claramente que o usuário não foi detectado
- `'(UTC)'`: Indica claramente que o fallback para UTC foi usado

### 4. Encoding UTF-8

Suporta caracteres especiais em nomes de branches e usuários (ex: acentos, emojis).

---

## Limitações Conhecidas

### 1. Detached HEAD

Se o repositório estiver em estado "detached HEAD", `get_git_branch()` retornará o hash do commit em vez do nome da branch.

**Mitigação:** Documentar comportamento esperado.

### 2. Submodules Git

Em submodules, a detecção de branch pode retornar a branch do submodule, não do repositório principal.

**Mitigação:** Comportamento esperado e documentado.

### 3. Horário de Verão

O timezone `America/Sao_Paulo` considera horário de verão automaticamente via pytz. Se pytz não estiver disponível, o fallback usa UTC sem considerar horário de verão.

**Mitigação:** Instalar pytz conforme `requirements.txt`.

---

## Evolução Futura

### Melhorias Planejadas

1. **Cache de Metadados:** Cachear branch e usuário para evitar múltiplas chamadas Git
2. **Detecção de Submodules:** Detectar e reportar quando em submodule
3. **Suporte a Múltiplos Timezones:** Permitir configuração de timezone via variável de ambiente
4. **Logging de Erros:** Registrar erros em arquivo de log para debugging

---

## Referências

- [Git Documentation](https://git-scm.com/docs)
- [Python subprocess](https://docs.python.org/3/library/subprocess.html)
- [pytz Documentation](https://pythonhosted.org/pytz/)
- Design do Prompt Logging: `.kiro/specs/prompt-logging/design.md`

---

**Versão:** 1.0.0  
**Data:** 2026-04-30  
**Autor:** Sistema de Prompt Logging
