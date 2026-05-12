"""
Utilitários para geração de relatórios.

Centraliza o caminho da pasta de relatórios e garante sua criação.
"""

import os

# Pasta raiz de todos os relatórios do backend
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")


def ensure_reports_dir() -> str:
    """
    Garante que a pasta backend/reports/ existe e retorna o caminho.

    Returns:
        Caminho absoluto da pasta de relatórios.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)
    return REPORTS_DIR


def report_path(filename: str) -> str:
    """
    Retorna o caminho completo de um arquivo de relatório.

    Args:
        filename: Nome do arquivo (ex: "banco_analise_nulos.csv").

    Returns:
        Caminho completo em backend/reports/<filename>.

    Exemplo:
        >>> path = report_path("banco_analise_nulos.csv")
        >>> # backend/reports/banco_analise_nulos.csv
    """
    ensure_reports_dir()
    return os.path.join(REPORTS_DIR, filename)
