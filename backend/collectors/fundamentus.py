"""
Coletor de indicadores fundamentalistas via biblioteca fundamentus.

Responsável por coletar indicadores específicos do mercado brasileiro (B3),
complementando os dados do yfinance com métricas como ROE, ROIC, P/L, P/VP,
Margem Líquida e Dívida Líquida/EBITDA.

Uso:
    from backend.collectors.fundamentus import get_fundamentals, get_sector

    fundamentals = get_fundamentals("PETR4")
    sector = get_sector("PETR4")

Formato dos dados retornados pelo fundamentus 0.3.x:
    - Campos de valuation (PL, PVP, EV_EBITDA, etc.): string inteira ×100
      Ex: "545" = P/L 5.45, "132" = P/VP 1.32
    - Percentuais (ROE, Margem, DY): string com "%" e ponto decimal
      Ex: "24.2%" = ROE 24.2% = 0.242 em decimal
    - Valores monetários (Cotacao, Patrim_Liq, etc.): float ou string numérica
"""

import logging
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

# Mapeamento de colunas do fundamentus para nomes padronizados do sistema
_COLUMN_MAP = {
    # Valuation (vêm como inteiro ×100 — ex: "545" = 5.45)
    "PL":              "pe_ratio",
    "PVP":             "pb_ratio",
    "PEBIT":           "p_ebit",
    "PSR":             "psr",
    "PAtivos":         "p_assets",
    "PCap_Giro":       "p_working_capital",
    "PAtiv_Circ_Liq":  "p_net_current_assets",
    "EV_EBIT":         "ev_ebit",
    "EV_EBITDA":       "ev_ebitda",
    # Rentabilidade (vêm como percentual — ex: "24.2%" = 0.242)
    "ROE":             "roe",
    "ROIC":            "roic",
    "Marg_Liquida":    "net_margin",
    "Marg_EBIT":       "ebit_margin",
    "Marg_Bruta":      "gross_margin",
    "EBIT_Ativo":      "ebit_assets",
    # Endividamento
    "Div_Liq_Patrim":  "debt_equity",
    "Liquidez_Corr":   "current_ratio",
    # Crescimento (percentual)
    "Cres_Rec_5a":     "revenue_growth_5y",
    # Dividendos (percentual)
    "Div_Yield":       "dividend_yield",
    # Outros
    "Giro_Ativos":     "asset_turnover",
    "LPA":             "eps",
    "VPA":             "book_value_per_share",
    "Div_Liquida":     "net_debt",
    "Patrim_Liq":      "total_equity",
    "Receita_Liquida_12m": "revenue",
    "Lucro_Liquido_12m":   "net_income",
    "Cotacao":         "current_price",
}

# Campos de valuation que o fundamentus retorna como inteiro ×100
# Ex: "545" = P/L 5.45, "132" = P/VP 1.32, "835" = LPA 8.35
_VALUATION_COLS = frozenset({
    "PL", "PVP", "PEBIT", "PSR", "PAtivos", "PCap_Giro",
    "PAtiv_Circ_Liq", "EV_EBIT", "EV_EBITDA",
    # Outros campos que também vêm ×100
    "LPA", "VPA", "Div_Liq_Patrim", "Liquidez_Corr", "Giro_Ativos", "EBIT_Ativo",
})


def get_fundamentals(ticker: str) -> dict:
    """
    Coleta indicadores fundamentalistas de uma ação da B3 via fundamentus.

    Args:
        ticker: Símbolo do ativo (ex: PETR4, VALE3). Apenas ações da B3.

    Returns:
        Dicionário com indicadores normalizados:
        - pe_ratio: P/L (Preço / Lucro)
        - pb_ratio: P/VP (Preço / Valor Patrimonial)
        - roe: Retorno sobre Patrimônio (decimal, ex: 0.242 = 24.2%)
        - roic: Retorno sobre Capital Investido (decimal)
        - net_margin: Margem Líquida (decimal)
        - ev_ebitda: EV/EBITDA
        - dividend_yield: Dividend Yield (decimal)
        - revenue_growth_5y: Crescimento de receita em 5 anos (decimal)
        - raw: Series original do fundamentus

    Raises:
        ValueError: Se o ticker for inválido ou não for uma ação da B3.
        RuntimeError: Se houver erro na comunicação com o fundamentus.
    """
    ticker = ticker.upper().strip()

    try:
        import fundamentus  # type: ignore

        result = fundamentus.get_papel(ticker)

        if isinstance(result, pd.DataFrame):
            if result.empty:
                raise ValueError(
                    f"Ticker '{ticker}' não encontrado no fundamentus. "
                    "Verifique se é uma ação da B3."
                )
            row = result.iloc[0]
        else:
            row = result

        normalized = _normalize_fundamentus_data(row, ticker)
        logger.info("Indicadores coletados para %s via fundamentus", ticker)
        return normalized

    except ValueError:
        raise
    except ImportError:
        logger.error("Biblioteca 'fundamentus' não instalada. Execute: pip install fundamentus")
        raise RuntimeError("Biblioteca 'fundamentus' não instalada.")
    except Exception as exc:
        logger.error("Erro ao coletar fundamentus para %s: %s", ticker, exc)
        raise RuntimeError(f"Falha ao coletar indicadores de '{ticker}': {exc}") from exc


def get_sector(ticker: str) -> Optional[str]:
    """
    Retorna o setor da empresa a partir dos dados do fundamentus.

    Args:
        ticker: Símbolo do ativo (ex: PETR4)

    Returns:
        Nome do setor ou None se não disponível.
    """
    ticker = ticker.upper().strip()

    try:
        import fundamentus  # type: ignore

        result = fundamentus.get_papel(ticker)

        if result is None or (isinstance(result, pd.DataFrame) and result.empty):
            logger.warning("Setor não encontrado para %s", ticker)
            return None

        row = result.iloc[0] if isinstance(result, pd.DataFrame) else result

        for col in ["Setor", "setor", "Segmento", "segmento"]:
            if isinstance(row, pd.Series) and col in row.index:
                val = str(row[col]).strip()
                if val and val not in ("nan", "-", ""):
                    return val

        return None

    except Exception as exc:
        logger.warning("Erro ao obter setor de %s: %s", ticker, exc)
        return None


def get_all_tickers() -> pd.DataFrame:
    """
    Retorna todos os tickers disponíveis no fundamentus com seus indicadores.

    Returns:
        DataFrame com todos os tickers e seus indicadores.
        Retorna DataFrame vazio em caso de falha.
    """
    try:
        import fundamentus  # type: ignore

        df = fundamentus.get_resultado()

        if df is None or df.empty:
            logger.warning("Nenhum dado retornado pelo fundamentus.get_resultado()")
            return pd.DataFrame()

        logger.info("Total de tickers coletados do fundamentus: %d", len(df))
        return df

    except Exception as exc:
        logger.error("Erro ao coletar todos os tickers do fundamentus: %s", exc)
        return pd.DataFrame()


def _normalize_fundamentus_data(row: pd.Series, ticker: str) -> dict:
    """
    Normaliza os dados brutos do fundamentus para o formato padrão do sistema.
    """
    normalized: dict = {"ticker": ticker, "raw": row}

    for original_col, system_col in _COLUMN_MAP.items():
        is_valuation = original_col in _VALUATION_COLS
        value = _safe_get(row, original_col,
                          zero_is_null=is_valuation,
                          divide_100=is_valuation)
        normalized[system_col] = value

    return normalized


def _safe_get(row: pd.Series, key: str, zero_is_null: bool = False,
              divide_100: bool = False) -> Optional[float]:
    """
    Extrai e converte um valor de uma linha do fundamentus com segurança.

    Regras de conversão:
    - Campos de valuation (divide_100=True): string inteira ×100
        "545" → 545.0 / 100 = 5.45
        "000" → None (dado ausente)
    - Percentuais: string com "%" e ponto decimal
        "24.2%" → remove "%" e "." → "242" → 242.0 / 1000 = 0.242
        "7.0%"  → "70"  → 70.0  / 1000 = 0.07
        "-5.3%" → "-53" → -53.0 / 1000 = -0.053
    - Valores monetários: float ou string numérica padrão
        45.47 → 45.47
        "1.234,56" → remove "." → "1234,56" → replace "," → "1234.56" → 1234.56

    Args:
        row: Linha do DataFrame.
        key: Nome da coluna.
        zero_is_null: Se True, trata 0.0 como None.
        divide_100: Se True, divide por 100 (campos de valuation ×100).

    Returns:
        Float normalizado ou None.
    """
    try:
        if isinstance(row, pd.Series) and key not in row.index:
            return None

        value = row[key] if isinstance(row, pd.Series) else getattr(row, key, None)

        if value is None or (isinstance(value, float) and pd.isna(value)):
            return None

        # Valor já numérico (float/int)
        if isinstance(value, (int, float)):
            num = float(value)
            if zero_is_null and num == 0.0:
                return None
            return num / 100 if divide_100 else num

        # Converte string
        value_str = str(value).strip()
        if not value_str or value_str in ("-", "N/A", "", "000"):
            return None

        is_percent = value_str.endswith("%")

        # Remove separador de milhar (ponto) e símbolo de percentual
        # Substitui vírgula decimal por ponto
        clean = value_str.replace("%", "").replace(".", "").replace(",", ".").strip()

        result = float(clean)

        if zero_is_null and result == 0.0:
            return None

        if is_percent:
            # "24.2%" → clean="242" → 242.0 → /1000 = 0.242
            # O replace(".", "") transforma "24.2" em "242" (remove o ponto decimal),
            # então o valor está ×10 em relação ao percentual real.
            # Para converter para decimal: /10 (desfaz o ×10) /100 (% → decimal) = /1000
            result = result / 1000
        elif divide_100:
            result = result / 100

        return result

    except (ValueError, TypeError, AttributeError):
        return None
