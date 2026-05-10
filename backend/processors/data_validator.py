"""
Validação de ranges de indicadores fundamentalistas.

Garante que valores fora dos ranges esperados sejam detectados antes
da persistência no banco, evitando dados corrompidos que distorcem o score.

Ranges definidos em .kiro/steering/compliance.md e docs/compliance.md.

Uso:
    from backend.processors.data_validator import validate_indicators

    clean, anomalies = validate_indicators(indicators, asset_type="stock")
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Ranges válidos por tipo de ativo
# ---------------------------------------------------------------------------

# Formato: campo -> (min, max, log_threshold)
# log_threshold: valor a partir do qual loga anomalia (None = usa min/max)
_STOCK_RANGES: dict[str, tuple] = {
    "roe":                   (-5.0,   5.0,   None),
    "roic":                  (-5.0,   5.0,   None),
    "net_margin":            (-2.0,   1.0,   None),
    "pe_ratio":              (-500,   500,   None),
    "pb_ratio":              (0,      100,   50),
    "debt_ebitda":           (-50,    50,    None),
    "ev_ebitda":             (0,      200,   100),
    "dividend_yield":        (0,      1.0,   0.5),
    "net_income_growth_yoy": (-1.0,   10.0,  None),
    "revenue_growth_yoy":    (-1.0,   10.0,  None),
}

_FII_RANGES: dict[str, tuple] = {
    "pb_ratio":              (0,      10,    5),
    "pe_ratio":              (0,      100,   50),
    "dividend_yield":        (0,      1.0,   0.5),
    "dividend_growth_yoy":   (-1.0,   5.0,   None),
}


# ---------------------------------------------------------------------------
# Funções de validação
# ---------------------------------------------------------------------------


def validate_indicators(
    indicators: dict,
    asset_type: str,
    ticker: str = "unknown",
) -> tuple[dict, list[dict]]:
    """
    Valida os indicadores de um ativo contra os ranges esperados.

    Indicadores fora do range são removidos do dicionário retornado
    e registrados na lista de anomalias.

    Args:
        indicators: Dicionário com indicadores calculados.
        asset_type: "stock" ou "fii".
        ticker: Símbolo do ativo (para logging).

    Returns:
        (clean_indicators, anomalies):
        - clean_indicators: Dicionário com apenas os indicadores válidos.
        - anomalies: Lista de dicionários descrevendo cada anomalia encontrada.

    Exemplo:
        >>> clean, anomalies = validate_indicators({"roe": 0.18, "pe_ratio": 600}, "stock", "PETR4")
        >>> print(clean)   # {"roe": 0.18}  — pe_ratio removido
        >>> print(anomalies)  # [{"field": "pe_ratio", "value": 600, ...}]
    """
    ranges = _STOCK_RANGES if asset_type == "stock" else _FII_RANGES
    clean: dict = {}
    anomalies: list[dict] = []

    for field, value in indicators.items():
        if value is None:
            clean[field] = value
            continue

        if field not in ranges:
            # Campo sem range definido — passa sem validação
            clean[field] = value
            continue

        min_val, max_val, log_threshold = ranges[field]

        try:
            v = float(value)
        except (ValueError, TypeError):
            clean[field] = value
            continue

        # Verifica se está fora do range absoluto
        if v < min_val or v > max_val:
            anomaly = {
                "ticker": ticker,
                "asset_type": asset_type,
                "field": field,
                "value": v,
                "expected_range": f"[{min_val}, {max_val}]",
                "action": "removed",
            }
            anomalies.append(anomaly)
            logger.warning(
                "[COMPLIANCE] Anomalia em %s.%s: valor=%.4f fora do range [%s, %s] — removido",
                ticker, field, v, min_val, max_val,
            )
            # Não inclui no clean — valor inválido descartado
            continue

        # Verifica se está acima do threshold de log (mas ainda válido)
        if log_threshold is not None:
            if abs(v) > log_threshold:
                logger.info(
                    "[COMPLIANCE] Atenção em %s.%s: valor=%.4f acima do threshold de log (%.4f)",
                    ticker, field, v, log_threshold,
                )

        clean[field] = v

    if anomalies:
        logger.warning(
            "[COMPLIANCE] %s: %d anomalia(s) detectada(s) em %d indicadores",
            ticker, len(anomalies), len(indicators),
        )

    return clean, anomalies


def validate_and_log_batch(
    tickers_indicators: list[tuple[str, str, dict]],
) -> tuple[list[tuple[str, dict]], list[dict]]:
    """
    Valida indicadores para um lote de tickers.

    Args:
        tickers_indicators: Lista de (ticker, asset_type, indicators).

    Returns:
        (clean_list, all_anomalies):
        - clean_list: Lista de (ticker, clean_indicators).
        - all_anomalies: Todas as anomalias encontradas no lote.
    """
    clean_list = []
    all_anomalies = []

    for ticker, asset_type, indicators in tickers_indicators:
        clean, anomalies = validate_indicators(indicators, asset_type, ticker)
        clean_list.append((ticker, clean))
        all_anomalies.extend(anomalies)

    if all_anomalies:
        logger.warning(
            "[COMPLIANCE] Lote: %d anomalia(s) em %d tickers",
            len(all_anomalies), len(tickers_indicators),
        )

    return clean_list, all_anomalies


def is_valid_ticker_symbol(symbol: str) -> bool:
    """
    Valida o formato de um ticker da B3.

    Aceita: PETR4, VALE3, HGLG11, WEGE3F (com sufixo F para fracionário)

    Args:
        symbol: Símbolo a validar.

    Returns:
        True se o formato for válido.
    """
    import re
    pattern = re.compile(r"^[A-Z]{4}\d{1,2}(F)?$")
    return bool(pattern.match(symbol.upper().strip()))


def generate_anomaly_report(anomalies: list[dict], output_path: str = None) -> None:
    """
    Gera relatório CSV de anomalias detectadas na validação.

    Args:
        anomalies: Lista de anomalias retornadas por validate_indicators.
        output_path: Caminho do CSV. Padrão: backend/reports/relatorio_anomalias.csv
    """
    from backend.scripts._report_utils import report_path
    if output_path is None:
        output_path = report_path("relatorio_anomalias.csv")
    if not anomalies:
        logger.info("[COMPLIANCE] Nenhuma anomalia para reportar.")
        return

    import pandas as pd
    df = pd.DataFrame(anomalies)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    logger.info("[COMPLIANCE] Relatório de anomalias: %s (%d registros)", output_path, len(df))
