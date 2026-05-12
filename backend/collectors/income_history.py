"""
Coleta de histórico de DRE via yfinance para cálculo de crescimento YoY.

Responsável por extrair o histórico anual de lucro líquido e receita
de ações da B3, calculando o CAGR (Compound Annual Growth Rate).

Uso:
    from backend.collectors.income_history import get_income_growth

    growth = get_income_growth("PETR4")
    print(growth["net_income_growth_yoy"])   # ex: 0.12 = 12% a.a.
    print(growth["revenue_growth_yoy"])      # ex: 0.08 = 8% a.a.
"""

import logging
from typing import Optional

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

_B3_SUFFIX = ".SA"

# Nomes possíveis da linha de Net Income no yfinance (varia por empresa)
_NET_INCOME_KEYS = [
    "net income",
    "net income from continuing operations",
    "net income common stockholders",
    "normalized income",
]

# Nomes possíveis da linha de Receita
_REVENUE_KEYS = [
    "total revenue",
    "net revenue",
    "revenue",
    "operating revenue",
]


def get_income_growth(symbol: str) -> dict:
    """
    Coleta histórico de DRE e calcula CAGR de lucro líquido e receita.

    Args:
        symbol: Símbolo da ação (ex: PETR4). Apenas ações — FIIs usam dividendos.

    Returns:
        Dicionário com:
        - net_income_growth_yoy: CAGR do lucro líquido (decimal, ex: 0.12)
        - revenue_growth_yoy: CAGR da receita (decimal, ex: 0.08)
        - net_income_history: Lista de lucros anuais (mais recente primeiro)
        - revenue_history: Lista de receitas anuais (mais recente primeiro)
        - years_available: Número de anos com dados
        - source: "yfinance"

        Campos são None se dados insuficientes (< 2 anos).

    Exemplo:
        >>> growth = get_income_growth("WEGE3")
        >>> print(f"Crescimento lucro: {growth['net_income_growth_yoy']:.1%}")
        Crescimento lucro: 11.0%
    """
    normalized = symbol.upper().strip()
    if not normalized.endswith(_B3_SUFFIX):
        normalized += _B3_SUFFIX

    try:
        stock = yf.Ticker(normalized)
        income_stmt = stock.income_stmt

        if income_stmt is None or income_stmt.empty:
            logger.debug("DRE vazio para %s", symbol)
            return _empty_result()

        net_income_history = _extract_series(income_stmt, _NET_INCOME_KEYS)
        revenue_history = _extract_series(income_stmt, _REVENUE_KEYS)

        net_income_cagr = _calculate_cagr(net_income_history)
        revenue_cagr = _calculate_cagr(revenue_history)

        years = max(
            len(net_income_history) if net_income_history else 0,
            len(revenue_history) if revenue_history else 0,
        )

        if net_income_cagr is not None or revenue_cagr is not None:
            logger.debug(
                "%s | Lucro CAGR: %s | Receita CAGR: %s | Anos: %d",
                symbol,
                f"{net_income_cagr:.1%}" if net_income_cagr else "N/A",
                f"{revenue_cagr:.1%}" if revenue_cagr else "N/A",
                years,
            )

        return {
            "net_income_growth_yoy": net_income_cagr,
            "revenue_growth_yoy": revenue_cagr,
            "net_income_history": net_income_history,
            "revenue_history": revenue_history,
            "years_available": years,
            "source": "yfinance",
        }

    except Exception as exc:
        logger.debug("Erro ao coletar histórico DRE de %s: %s", symbol, exc)
        return _empty_result()


def _extract_series(df: pd.DataFrame, keys: list[str]) -> list[float]:
    """
    Extrai uma série temporal de uma linha do DataFrame de DRE.

    Tenta cada chave em ordem até encontrar uma com dados.
    Retorna lista do mais recente para o mais antigo.

    Args:
        df: DataFrame do income_stmt do yfinance.
        keys: Lista de nomes possíveis da linha (case-insensitive).

    Returns:
        Lista de floats ou lista vazia se não encontrado.
    """
    for key in keys:
        matches = [
            idx for idx in df.index
            if key.lower() in str(idx).lower()
        ]
        if not matches:
            continue

        row = df.loc[matches[0]]
        values = []
        for v in row:
            if v is not None and not (isinstance(v, float) and pd.isna(v)):
                try:
                    values.append(float(v))
                except (ValueError, TypeError):
                    pass

        if len(values) >= 2:
            return values  # yfinance já retorna do mais recente para o mais antigo

    return []


def _calculate_cagr(values: list[float]) -> Optional[float]:
    """
    Calcula o CAGR a partir de uma lista de valores anuais.

    Args:
        values: Lista de valores do mais recente para o mais antigo.

    Returns:
        CAGR como decimal ou None se dados insuficientes/inválidos.
    """
    if not values or len(values) < 2:
        return None

    # Remove zeros e None
    clean = [v for v in values if v is not None and v != 0]
    if len(clean) < 2:
        return None

    final_value = clean[0]    # Mais recente
    initial_value = clean[-1]  # Mais antigo
    n_years = len(clean) - 1

    # Não calcula CAGR com valores negativos (empresa com prejuízo histórico)
    if initial_value <= 0 or final_value <= 0:
        # Retorna crescimento simples se apenas o mais recente for positivo
        if final_value > 0 and initial_value < 0:
            return None  # Não representativo
        return None

    try:
        cagr = (final_value / initial_value) ** (1 / n_years) - 1
        return round(cagr, 6)
    except (ZeroDivisionError, ValueError):
        return None


def _empty_result() -> dict:
    return {
        "net_income_growth_yoy": None,
        "revenue_growth_yoy": None,
        "net_income_history": [],
        "revenue_history": [],
        "years_available": 0,
        "source": "yfinance",
    }
