#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de logging de prompts do Kiro.

Este script captura automaticamente prompts executados no Kiro e os registra
em arquivos Markdown organizados por branch Git. É acionado via hook do Kiro
no evento 'promptSubmit'.

Funcionalidades:
- Detecta a branch Git atual
- Obtém o nome do usuário Git
- Gera timestamp no horário de Brasília (America/Sao_Paulo)
- Tenta capturar o conteúdo do prompt (via env ou stdin)
- Persiste logs em .kiro/prompt-logs/<branch-name>.md

Uso:
    Este script é executado automaticamente pelo hook do Kiro.
    Não requer execução manual.

Dependências:
    - Python 3.8+
    - pytz (para timezone de Brasília)
    - Git instalado e configurado

Autor: Sistema de Prompt Logging
Versão: 1.0.0
"""

import os
import sys
import subprocess
from datetime import datetime
import pytz


def get_git_branch():
    """
    Retorna a branch Git atual.
    
    Returns:
        str: Nome da branch atual ou 'unknown-branch' em caso de erro.
    
    Tratamento de erros:
        - Se Git não estiver instalado: retorna 'unknown-branch'
        - Se não estiver em um repositório Git: retorna 'unknown-branch'
        - Se houver qualquer outro erro: retorna 'unknown-branch'
    """
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            check=True,
            timeout=5  # Timeout de 5 segundos para evitar travamentos
        )
        branch = result.stdout.strip()
        return branch if branch else 'unknown-branch'
    except subprocess.CalledProcessError:
        # Git retornou erro (não é um repositório, etc.)
        return 'unknown-branch'
    except subprocess.TimeoutExpired:
        # Comando Git demorou muito
        return 'unknown-branch'
    except FileNotFoundError:
        # Git não está instalado
        return 'unknown-branch'
    except Exception:
        # Qualquer outro erro inesperado
        return 'unknown-branch'


def get_git_user():
    """
    Retorna o nome do usuário Git configurado.
    
    Returns:
        str: Nome do usuário Git ou 'Unknown User' em caso de erro.
    
    Tratamento de erros:
        - Se Git não estiver instalado: retorna 'Unknown User'
        - Se user.name não estiver configurado: retorna 'Unknown User'
        - Se houver qualquer outro erro: retorna 'Unknown User'
    """
    try:
        result = subprocess.run(
            ['git', 'config', 'user.name'],
            capture_output=True,
            text=True,
            check=True,
            timeout=5  # Timeout de 5 segundos
        )
        user = result.stdout.strip()
        return user if user else 'Unknown User'
    except subprocess.CalledProcessError:
        # Git config não retornou user.name (não configurado)
        return 'Unknown User'
    except subprocess.TimeoutExpired:
        # Comando Git demorou muito
        return 'Unknown User'
    except FileNotFoundError:
        # Git não está instalado
        return 'Unknown User'
    except Exception:
        # Qualquer outro erro inesperado
        return 'Unknown User'


def get_brasilia_timestamp():
    """
    Retorna timestamp formatado no horário de Brasília (America/Sao_Paulo).
    
    Returns:
        str: Timestamp no formato 'YYYY-MM-DD HH:MM:SS' ou timestamp UTC em caso de erro.
    
    Tratamento de erros:
        - Se pytz não estiver disponível: usa UTC como fallback
        - Se timezone de Brasília não for encontrado: usa UTC como fallback
        - Se houver qualquer outro erro: usa UTC como fallback
    
    Nota:
        O timezone America/Sao_Paulo considera automaticamente horário de verão
        quando aplicável.
    """
    try:
        tz = pytz.timezone('America/Sao_Paulo')
        now = datetime.now(tz)
        return now.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        # Fallback para UTC se houver qualquer problema com pytz
        now = datetime.utcnow()
        return now.strftime('%Y-%m-%d %H:%M:%S') + ' (UTC)'


def get_prompt_content():
    """
    Tenta capturar o conteúdo do prompt usando múltiplas estratégias.
    
    Estratégias (em ordem de prioridade):
    1. Argumentos de linha de comando (sys.argv)
    2. Variável de ambiente KIRO_PROMPT (se disponível)
    3. Leitura de stdin (se não for TTY e houver conteúdo)
    4. Retorna None se nenhuma estratégia funcionar (será filtrado)
    
    Returns:
        str or None: Conteúdo do prompt ou None se não disponível.
    
    Nota:
        A disponibilidade do conteúdo do prompt depende de como o Kiro
        expõe informações aos hooks. Se nenhuma estratégia funcionar,
        retorna None para que o log seja filtrado.
    """
    # Estratégia 1: Argumentos de linha de comando
    try:
        if len(sys.argv) > 1:
            # Junta todos os argumentos (exceto o nome do script)
            prompt = ' '.join(sys.argv[1:]).strip()
            if prompt:
                return prompt
    except Exception:
        pass
    
    # Estratégia 2: Variável de ambiente KIRO_PROMPT
    try:
        prompt = os.environ.get('KIRO_PROMPT')
        if prompt and prompt.strip():
            return prompt.strip()
    except Exception:
        pass
    
    # Estratégia 3: Leitura de stdin (se não for TTY)
    try:
        if not sys.stdin.isatty():
            prompt = sys.stdin.read().strip()
            if prompt:
                return prompt
    except Exception:
        pass
    
    # Estratégia 4: Retorna None (será filtrado)
    return None


def is_trivial_prompt(content):
    """
    Verifica se o prompt é trivial e não deve ser registrado.
    
    Prompts triviais incluem:
    - Confirmações simples (sim, não, ok, yes, no)
    - Respostas muito curtas (< 10 caracteres)
    - Comandos de navegação (next, back, continue)
    - Conteúdo vazio ou None
    
    Args:
        content (str or None): Conteúdo do prompt a ser verificado.
    
    Returns:
        bool: True se o prompt é trivial, False caso contrário.
    """
    if content is None:
        return True
    
    content_lower = content.lower().strip()
    
    # Lista de padrões triviais
    trivial_patterns = [
        # Confirmações
        'sim', 'não', 'nao', 'ok', 'yes', 'no', 'y', 'n',
        # Comandos de navegação
        'next', 'back', 'continue', 'skip', 'cancel',
        # Respostas curtas comuns
        'done', 'finish', 'stop', 'start', 'run',
        # Números isolados
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
    ]
    
    # Verifica se é exatamente um padrão trivial
    if content_lower in trivial_patterns:
        return True
    
    # Verifica se é muito curto (< 10 caracteres)
    if len(content.strip()) < 10:
        return True
    
    return False


def sanitize_branch_name(branch):
    """
    Sanitiza nome da branch para uso em nome de arquivo.
    
    Converte caracteres especiais que não são válidos em nomes de arquivo
    para hífens, garantindo compatibilidade com sistemas de arquivos.
    
    Args:
        branch (str): Nome da branch Git original.
    
    Returns:
        str: Nome sanitizado válido para uso em nome de arquivo.
    
    Transformações aplicadas:
        - '/' → '-' (separadores de diretório em branches como feature/auth)
        - '\\' → '-' (separadores de diretório no Windows)
        - Outros caracteres especiais problemáticos são preservados por ora
    
    Exemplos:
        >>> sanitize_branch_name('feature/auth')
        'feature-auth'
        >>> sanitize_branch_name('bugfix/crash-fix')
        'bugfix-crash-fix'
        >>> sanitize_branch_name('main')
        'main'
    """
    if not branch:
        return 'unknown-branch'
    
    # Substitui barras por hífens
    sanitized = branch.replace('/', '-').replace('\\', '-')
    
    # Remove espaços (se houver) e substitui por hífens
    sanitized = sanitized.replace(' ', '-')
    
    # Remove caracteres potencialmente problemáticos em nomes de arquivo
    # Mantém: letras, números, hífens, underscores, pontos
    import re
    sanitized = re.sub(r'[^a-zA-Z0-9\-_.]', '-', sanitized)
    
    # Remove hífens duplicados
    sanitized = re.sub(r'-+', '-', sanitized)
    
    # Remove hífens no início e fim
    sanitized = sanitized.strip('-')
    
    return sanitized if sanitized else 'unknown-branch'


def format_log_entry(branch, user, timestamp, prompt_content):
    """
    Formata entrada de log no padrão Markdown estruturado.
    
    Gera uma entrada de log completa seguindo o formato definido no design:
    - Cabeçalho com título extraído do prompt
    - Metadados (responsável, branch, data/hora)
    - Conteúdo do prompt em bloco de código
    - Separador visual entre entradas
    
    Args:
        branch (str): Nome da branch Git.
        user (str): Nome do usuário Git.
        timestamp (str): Timestamp formatado.
        prompt_content (str): Conteúdo completo do prompt.
    
    Returns:
        str: Entrada de log formatada em Markdown.
    
    Formato de saída:
        ## Prompt: <título>
        - Responsável: <user>
        - Branch: <branch>
        - Data/hora: <timestamp> (Brasília)
        
        ### Prompt original
        ```
        <prompt_content>
        ```
        
        ---
    """
    # Extrai título do prompt (primeiras 50 caracteres)
    title = prompt_content[:50] if len(prompt_content) <= 50 else prompt_content[:50] + '...'
    
    # Remove quebras de linha do título para mantê-lo em uma linha
    title = title.replace('\n', ' ').replace('\r', ' ').strip()
    
    # Se o título estiver vazio ou for o placeholder, usa um título padrão
    if not title or title == "[Conteúdo do prompt não capturado automaticamente]":
        title = "Prompt não capturado"
    
    # Formata a entrada completa
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
    """
    Função principal de logging de prompts.
    
    Orquestra todo o processo de captura e persistência de logs:
    1. Coleta metadados (branch, usuário, timestamp)
    2. Captura conteúdo do prompt
    3. Filtra prompts triviais (confirmações, respostas curtas)
    4. Determina arquivo de log apropriado
    5. Cria diretório e arquivo se necessário
    6. Adiciona cabeçalho na primeira entrada
    7. Formata e persiste entrada de log
    
    Tratamento de erros:
        Esta função implementa tratamento de erros gracioso para garantir
        que falhas no logging NUNCA bloqueiem a execução do Kiro.
        Erros são registrados em stderr mas não levantam exceções.
    
    Fluxo de execução:
        - Sucesso: Log é persistido silenciosamente (sem output)
        - Prompt trivial: Ignorado silenciosamente (sem log)
        - Falha: Mensagem de erro em stderr, execução continua normalmente
    
    Efeitos colaterais:
        - Cria diretório .kiro/prompt-logs/ se não existir
        - Cria arquivo <branch-name>.md se não existir
        - Adiciona entrada ao arquivo em modo append
    """
    try:
        # 1. Coleta metadados
        branch = get_git_branch()
        user = get_git_user()
        timestamp = get_brasilia_timestamp()
        prompt_content = get_prompt_content()
        
        # 2. Filtra prompts triviais
        if is_trivial_prompt(prompt_content):
            # Ignora silenciosamente - não registra prompts triviais
            return
        
        # 3. Determina caminho do arquivo de log
        sanitized_branch = sanitize_branch_name(branch)
        log_dir = '.kiro/prompt-logs'
        log_file = os.path.join(log_dir, f'{sanitized_branch}.md')
        
        # 4. Cria diretório se não existir
        try:
            os.makedirs(log_dir, exist_ok=True)
        except OSError as e:
            # Falha ao criar diretório - registra erro mas não bloqueia
            print(f"[Prompt Logger] Erro ao criar diretório {log_dir}: {e}", file=sys.stderr)
            return
        
        # 5. Adiciona cabeçalho se arquivo não existir
        file_is_new = not os.path.exists(log_file)
        
        if file_is_new:
            try:
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write(f'# Prompt Logs: {branch}\n\n')
                    f.write('Histórico de prompts executados no Kiro nesta branch.\n\n')
                    f.write('---\n\n')
            except (OSError, IOError) as e:
                # Falha ao criar arquivo - registra erro mas não bloqueia
                print(f"[Prompt Logger] Erro ao criar arquivo {log_file}: {e}", file=sys.stderr)
                return
        
        # 6. Formata entrada de log
        entry = format_log_entry(branch, user, timestamp, prompt_content)
        
        # 7. Adiciona entrada ao arquivo (modo append)
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(entry)
        except (OSError, IOError) as e:
            # Falha ao escrever no arquivo - registra erro mas não bloqueia
            print(f"[Prompt Logger] Erro ao escrever em {log_file}: {e}", file=sys.stderr)
            return
        
        # Sucesso silencioso - não imprime nada para não poluir output do Kiro
        
    except Exception as e:
        # Captura qualquer erro inesperado para garantir que nunca bloqueamos o Kiro
        print(f"[Prompt Logger] Erro inesperado ao registrar prompt: {e}", file=sys.stderr)
        # Não levanta exceção - falha graciosamente


if __name__ == '__main__':
    log_prompt()
