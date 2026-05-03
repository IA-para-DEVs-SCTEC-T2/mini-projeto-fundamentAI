#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de logging de prompts do Kiro.

Captura metadados e registra prompts em arquivos Markdown organizados por branch Git.
Executado automaticamente pelo hook promptSubmit do Kiro.

Uso manual:
    python .kiro/scripts/log_prompt.py

Dependências:
    pip install pytz
"""

import os
import sys
import subprocess
from datetime import datetime

try:
    import pytz
    _HAS_PYTZ = True
except ImportError:
    _HAS_PYTZ = False


# ---------------------------------------------------------------------------
# Coleta de metadados
# ---------------------------------------------------------------------------


def get_git_branch() -> str:
    """
    Retorna a branch Git atual.

    Returns:
        Nome da branch ou 'unknown-branch' em caso de falha.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown-branch"


def get_git_user() -> str:
    """
    Retorna o nome do usuário Git configurado.

    Returns:
        Nome do usuário ou 'Unknown User' em caso de falha.
    """
    try:
        result = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True,
            text=True,
            check=True,
        )
        name = result.stdout.strip()
        return name if name else "Unknown User"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "Unknown User"


def get_brasilia_timestamp() -> str:
    """
    Retorna timestamp formatado no horário de Brasília (America/Sao_Paulo).

    Returns:
        String no formato 'YYYY-MM-DD HH:MM:SS'.
    """
    if _HAS_PYTZ:
        tz = pytz.timezone("America/Sao_Paulo")
        now = datetime.now(tz)
    else:
        # Fallback: UTC sem pytz (com aviso)
        now = datetime.utcnow()
        print("[Prompt Logger] Aviso: pytz não instalado. Usando UTC. Execute: pip install pytz", file=sys.stderr)

    return now.strftime("%Y-%m-%d %H:%M:%S")


def get_prompt_content() -> str:
    """
    Tenta capturar o conteúdo do prompt via múltiplas estratégias.

    Estratégias (em ordem de prioridade):
    1. Variável de ambiente KIRO_PROMPT
    2. Stdin (se não for TTY — pipe)
    3. Placeholder se não disponível

    Returns:
        Conteúdo do prompt ou placeholder.
    """
    # Estratégia 1: variável de ambiente
    prompt = os.environ.get("KIRO_PROMPT", "").strip()
    if prompt:
        return prompt

    # Estratégia 2: stdin (pipe)
    if not sys.stdin.isatty():
        try:
            content = sys.stdin.read().strip()
            if content:
                return content
        except Exception:
            pass

    # Estratégia 3: placeholder
    return "[Conteúdo do prompt não capturado automaticamente]"


# ---------------------------------------------------------------------------
# Formatação
# ---------------------------------------------------------------------------


def sanitize_branch_name(branch: str) -> str:
    """
    Sanitiza o nome da branch para uso como nome de arquivo.

    Converte '/' e '\\' em '-' para evitar criação de subdiretórios.

    Args:
        branch: Nome da branch Git.

    Returns:
        Nome sanitizado válido para sistema de arquivos.
    """
    return branch.replace("/", "-").replace("\\", "-")


def extract_title(prompt_content: str, max_length: int = 60) -> str:
    """
    Extrai um título curto do conteúdo do prompt.

    Args:
        prompt_content: Conteúdo completo do prompt.
        max_length: Comprimento máximo do título.

    Returns:
        Título truncado e limpo.
    """
    if prompt_content == "[Conteúdo do prompt não capturado automaticamente]":
        return "Prompt não capturado"

    # Pega a primeira linha não vazia
    first_line = ""
    for line in prompt_content.splitlines():
        line = line.strip()
        if line:
            first_line = line
            break

    if not first_line:
        first_line = prompt_content.strip()

    if len(first_line) > max_length:
        return first_line[:max_length].rstrip() + "..."

    return first_line


def format_log_entry(branch: str, user: str, timestamp: str, prompt_content: str) -> str:
    """
    Formata uma entrada de log no padrão Markdown definido na spec.

    Args:
        branch: Nome da branch Git.
        user: Nome do usuário Git.
        timestamp: Timestamp formatado (horário de Brasília).
        prompt_content: Conteúdo do prompt.

    Returns:
        String formatada em Markdown pronta para append.
    """
    title = extract_title(prompt_content)

    entry = (
        f"## Prompt: {title}\n"
        f"- Responsável: {user}\n"
        f"- Branch: {branch}\n"
        f"- Data/hora: {timestamp} (Brasília)\n"
        f"\n"
        f"### Prompt original\n"
        f"```\n"
        f"{prompt_content}\n"
        f"```\n"
        f"\n"
        f"---\n"
        f"\n"
    )
    return entry


def create_log_header(branch: str) -> str:
    """
    Cria o cabeçalho do arquivo de log para uma nova branch.

    Args:
        branch: Nome da branch Git.

    Returns:
        Cabeçalho em Markdown.
    """
    return (
        f"# Prompt Logs: {branch}\n"
        f"\n"
        f"Histórico de prompts executados no Kiro nesta branch.\n"
        f"\n"
        f"---\n"
        f"\n"
    )


# ---------------------------------------------------------------------------
# Persistência
# ---------------------------------------------------------------------------


def log_prompt() -> None:
    """
    Função principal: coleta metadados, formata e persiste o log.

    Trata todos os erros graciosamente — nunca bloqueia a execução do Kiro.
    """
    try:
        # Coleta metadados
        branch = get_git_branch()
        user = get_git_user()
        timestamp = get_brasilia_timestamp()
        prompt_content = get_prompt_content()

        # Determina caminho do arquivo de log
        sanitized_branch = sanitize_branch_name(branch)
        log_dir = ".kiro/prompt-logs"
        log_file = os.path.join(log_dir, f"{sanitized_branch}.md")

        # Cria diretório se não existir
        os.makedirs(log_dir, exist_ok=True)

        # Adiciona cabeçalho se arquivo não existir ainda
        is_new_file = not os.path.exists(log_file)

        with open(log_file, "a", encoding="utf-8") as f:
            if is_new_file:
                f.write(create_log_header(branch))

            entry = format_log_entry(branch, user, timestamp, prompt_content)
            f.write(entry)

        # Sucesso silencioso — não polui o output do Kiro

    except Exception as exc:
        # Nunca bloqueia o Kiro — apenas loga o erro em stderr
        print(f"[Prompt Logger] Erro ao registrar prompt: {exc}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    log_prompt()
