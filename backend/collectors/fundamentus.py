"""
Coletor de indicadores fundamentalistas via biblioteca fundamentus.

Responsável por coletar indicadores específicos do mercado brasileiro (B3),
complementando os dados do yfinance com métricas como ROE, ROIC, P/L, P/VP,
Margem Líquida e Dívida Líquida/EBITDA.

Uso:
    from backend.collectors.fundamentus import get_fundamentals, get_sector

    fundamentals = get_fundamentals("PETR4")
    sector = get_sector("PETR4")
"""

import logging
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

# Mapeamento de colunas do fundamentus para nomes padronizados do sistema
_COLUMN_MAP = {
    # Valuation
    "P/L": "pe_ratio",
    "P/VP": "pb_ratio",
    "P/EBIT": "p_ebit",
    "PSR": "psr",
    "P/Ativ": "p_assets",
    "P/Cap.Giro": "p_working_capital",
    "P/Ativ Circ.Liq": "p_net_current_assets",
    "EV/EBIT": "ev_ebit",
    "EV/EBITDA": "ev_ebitda",
    # Rentabilidade
    "ROE": "roe",
    "ROIC": "roic",
    "Mrg Liq": "net_margin",
    "Mrg EBIT": "ebit_margin",
    "Mrg. Bruta": "gross_margin",
    # Endividamento
    "Div.Br/ Patrim.": "debt_equity",
    "Liq. Corr.": "current_ratio",
    # Crescimento
    "Cresc. Rec.5a": "revenue_growth_5y",
    # Outros
    "Div.Yield": "dividend_yield",
    "Giro Ativos": "asset_turnover",
}


def get_fundamentals(ticker: str) -> dict:
    """
    Coleta indicadores fundamentalistas de uma ação da B3 via fundamentus.

    Args:
        ticker: Símbolo do ativo (ex: PETR4, VALE3). Apenas ações da B3.

    Returns:
        Dicionário com indicadores normalizados:
        - pe_ratio: P/L (Preço / Lucro)
        - pb_ratio: P/VP (Preço / Valor Patrimonial)
        - roe: Retorno sobre Patrimônio (decimal, ex: 0.15 = 15%)
        - roic: Retorno sobre Capital Investido (decimal)
        - net_margin: Margem Líquida (decimal)
        - debt_equity: Dívida Bruta / Patrimônio
        - dividend_yield: Dividend Yield (decimal)
        - revenue_growth_5y: Crescimento de receita em 5 anos (decimal)
        - raw: DataFrame original do fundamentus

    Raises:
        ValueError: Se o ticker for inválido ou não for uma ação da B3.
        RuntimeError: Se houver erro na comunicação com o fundamentus.

    Exemplo:
        >>> data = get_fundamentals("ITUB4")
        >>> print(f"ROE: {data['roe']:.1%}")
        ROE: 18.5%
    """
    ticker = ticker.upper().strip()

    try:
        import fundamentus  # type: ignore

        result = fundamentus.get_papel(ticker)

        if result is None or (isinstance(result, pd.DataFrame) and result.empty):
            raise ValueError(f"Ticker '{ticker}' não encontrado no fundamentus. Verifique se é uma ação da B3.")

        # fundamentus retorna um DataFrame com o ticker como índice
        if isinstance(result, pd.DataFrame):
            row = result.iloc[0] if len(result) > 0 else result
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

    Exemplo:
        >>> sector = get_sector("PETR4")
        >>> print(sector)
        "Petróleo, Gás e Biocombustíveis"
    """
    ticker = ticker.upper().strip()

    try:
        import fundamentus  # type: ignore

        result = fundamentus.get_papel(ticker)

        if result is None or (isinstance(result, pd.DataFrame) and result.empty):
            logger.warning("Setor não encontrado para %s", ticker)
            return None

        if isinstance(result, pd.DataFrame):
            row = result.iloc[0] if len(result) > 0 else result
        else:
            row = result

        # Tenta diferentes nomes de coluna para setor
        for col in ["Setor", "setor", "Segmento", "segmento"]:
            if hasattr(row, col) or (isinstance(row, pd.Series) and col in row.index):
                val = row[col] if isinstance(row, pd.Series) else getattr(row, col)
                if val and str(val).strip():
                    return str(val).strip()

        return None

    except Exception as exc:
        logger.warning("Erro ao obter setor de %s: %s", ticker, exc)
        return None


def get_all_tickers() -> pd.DataFrame:
    """
    Retorna todos os tickers disponíveis no fundamentus com seus indicadores.

    Útil para comparação setorial — permite obter médias do setor.

    Returns:
        DataFrame com todos os tickers e seus indicadores.
        Retorna DataFrame vazio em caso de falha.

    Exemplo:
        >>> all_tickers = get_all_tickers()
        >>> print(f"Total de tickers: {len(all_tickers)}")
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

    Converte percentuais de string para float decimal (ex: "15,3%" → 0.153).

    Args:
        row: Linha do DataFrame do fundamentus.
        ticker: Símbolo para logging.

    Returns:
        Dicionário com indicadores normalizados.
    """
    normalized: dict = {"ticker": ticker, "raw": row}

    for original_col, system_col in _COLUMN_MAP.items():
        value = _safe_get(row, original_col)
        normalized[system_col] = value

    return normalized


def _safe_get(row: pd.Series, key: str) -> Optional[float]:
    """
    Extrai e converte um valor de uma linha do fundamentus com segurança.

    Trata:
    - Percentuais com vírgula: "15,3%" → 0.153
    - Valores com vírgula decimal: "1.234,56" → 1234.56
    - Valores ausentes ou inválidos → None

    Args:
        row: Linha do DataFrame.
        key: Nome da coluna.

    Returns:
        Float normalizado ou None.
    """
    try:
        if isinstance(row, pd.Series) and key not in row.index:
            return None

        value = row[key] if isinstance(row, pd.Series) else getattr(row, key, None)

        if value is None or (isinstance(value, float) and pd.isna(value)):
            return None

        if isinstance(value, (int, float)):
            return float(value)

        # Converte string
        value_str = str(value).strip()
        if not value_str or value_str in ("-", "N/A", ""):
            return None

        is_percent = value_str.endswith("%")
        value_str = value_str.replace("%", "").replace(".", "").replace(",", ".").strip()

        result = float(value_str)

        # Percentuais do fundamentus já vêm como decimal (ex: 0.153 = 15.3%)
        # mas alguns podem vir como inteiro (ex: 15.3 = 15.3%)
        # Normaliza para decimal se necessário
        if is_percent and abs(result) > 1:
            result = result / 100

        return result

    except (ValueError, TypeError, AttributeError):
        return None
