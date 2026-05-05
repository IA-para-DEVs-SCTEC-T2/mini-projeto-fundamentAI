"""
Coletor de dados financeiros via yfinance.

Responsável por coletar cotações, histórico de preços e demonstrativos
financeiros (DRE e Balanço Patrimonial) de ações da B3.

Uso:
    from backend.collectors.yfinance import get_stock_quote, get_price_history, get_financial_statements

    quote = get_stock_quote("PETR4")
    history = get_price_history("PETR4", years=5)
    statements = get_financial_statements("PETR4")
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

# Sufixo da B3 no yfinance
_B3_SUFFIX = ".SA"


def _normalize_ticker(ticker: str) -> str:
    """
    Normaliza o ticker para o formato aceito pelo yfinance (ex: PETR4 → PETR4.SA).

    Args:
        ticker: Símbolo do ativo (ex: PETR4, VALE3, HGLG11)

    Returns:
        Ticker com sufixo .SA se ainda não tiver.
    """
    ticker = ticker.upper().strip()
    if not ticker.endswith(_B3_SUFFIX):
        ticker = ticker + _B3_SUFFIX
    return ticker


def get_stock_quote(ticker: str) -> dict:
    """
    Retorna a cotação atual de uma ação da B3.

    Args:
        ticker: Símbolo do ativo (ex: PETR4, VALE3)

    Returns:
        Dicionário com cotação atual, variação, volume e market cap.

    Raises:
        ValueError: Se o ticker for inválido ou não encontrado.
        RuntimeError: Se houver erro na comunicação com a API.

    Exemplo:
        >>> quote = get_stock_quote("PETR4")
        >>> print(quote["current_price"])
        38.50
    """
    normalized = _normalize_ticker(ticker)
    try:
        stock = yf.Ticker(normalized)
        info = stock.info

        if not info or info.get("regularMarketPrice") is None:
            # Tenta fast_info como fallback
            fast = stock.fast_info
            current_price = getattr(fast, "last_price", None)
            if current_price is None:
                raise ValueError(f"Ticker '{ticker}' não encontrado ou sem dados disponíveis.")
        else:
            current_price = info.get("regularMarketPrice") or info.get("currentPrice")

        return {
            "ticker": ticker.upper(),
            "current_price": current_price,
            "previous_close": info.get("previousClose"),
            "change_percent": info.get("regularMarketChangePercent"),
            "volume": info.get("regularMarketVolume"),
            "market_cap": info.get("marketCap"),
            "currency": info.get("currency", "BRL"),
            "collected_at": datetime.utcnow().isoformat(),
        }

    except ValueError:
        raise
    except Exception as exc:
        logger.error("Erro ao coletar cotação de %s: %s", ticker, exc)
        raise RuntimeError(f"Falha ao coletar cotação de '{ticker}': {exc}") from exc


def get_price_history(ticker: str, years: int = 5) -> pd.DataFrame:
    """
    Retorna o histórico de preços de fechamento ajustados.

    Args:
        ticker: Símbolo do ativo (ex: PETR4)
        years: Número de anos de histórico (padrão: 5)

    Returns:
        DataFrame com colunas: Date, Open, High, Low, Close, Volume.
        Retorna DataFrame vazio se não houver dados.

    Raises:
        ValueError: Se o ticker for inválido.
        RuntimeError: Se houver erro na comunicação com a API.

    Exemplo:
        >>> history = get_price_history("VALE3", years=3)
        >>> print(history.head())
    """
    normalized = _normalize_ticker(ticker)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=years * 365)

    try:
        stock = yf.Ticker(normalized)
        history = stock.history(
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
            auto_adjust=True,
        )

        if history.empty:
            logger.warning("Histórico vazio para %s", ticker)
            return pd.DataFrame()

        history.index = pd.to_datetime(history.index)
        history = history[["Open", "High", "Low", "Close", "Volume"]].copy()
        history.index.name = "Date"

        logger.info("Histórico coletado para %s: %d registros", ticker, len(history))
        return history

    except Exception as exc:
        logger.error("Erro ao coletar histórico de %s: %s", ticker, exc)
        raise RuntimeError(f"Falha ao coletar histórico de '{ticker}': {exc}") from exc


def get_financial_statements(ticker: str) -> dict[str, pd.DataFrame]:
    """
    Retorna os demonstrativos financeiros anuais (DRE e Balanço Patrimonial).

    Args:
        ticker: Símbolo do ativo (ex: PETR4)

    Returns:
        Dicionário com chaves:
        - "income_statement": DRE anual (DataFrame)
        - "balance_sheet": Balanço Patrimonial anual (DataFrame)
        - "cash_flow": Fluxo de Caixa anual (DataFrame)

        Cada DataFrame tem anos como colunas e linhas como itens financeiros.
        Retorna DataFrames vazios para demonstrativos indisponíveis.

    Raises:
        ValueError: Se o ticker for inválido.
        RuntimeError: Se houver erro na comunicação com a API.

    Exemplo:
        >>> statements = get_financial_statements("ITUB4")
        >>> dre = statements["income_statement"]
        >>> print(dre.loc["Net Income"])
    """
    normalized = _normalize_ticker(ticker)

    try:
        stock = yf.Ticker(normalized)

        income_stmt = _safe_get_dataframe(stock, "income_stmt", ticker, "DRE")
        balance_sheet = _safe_get_dataframe(stock, "balance_sheet", ticker, "Balanço")
        cash_flow = _safe_get_dataframe(stock, "cash_flow", ticker, "Fluxo de Caixa")

        logger.info(
            "Demonstrativos coletados para %s — DRE: %s, Balanço: %s, FC: %s",
            ticker,
            "ok" if not income_stmt.empty else "vazio",
            "ok" if not balance_sheet.empty else "vazio",
            "ok" if not cash_flow.empty else "vazio",
        )

        return {
            "income_statement": income_stmt,
            "balance_sheet": balance_sheet,
            "cash_flow": cash_flow,
        }

    except Exception as exc:
        logger.error("Erro ao coletar demonstrativos de %s: %s", ticker, exc)
        raise RuntimeError(f"Falha ao coletar demonstrativos de '{ticker}': {exc}") from exc


def _safe_get_dataframe(
    stock: yf.Ticker,
    attribute: str,
    ticker: str,
    label: str,
) -> pd.DataFrame:
    """
    Tenta obter um DataFrame de um atributo do yf.Ticker com tratamento de erro.

    Args:
        stock: Objeto yf.Ticker já instanciado.
        attribute: Nome do atributo (ex: "income_stmt").
        ticker: Símbolo para logging.
        label: Nome legível para logging.

    Returns:
        DataFrame ou DataFrame vazio em caso de falha.
    """
    try:
        df = getattr(stock, attribute, None)
        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            logger.warning("%s indisponível para %s", label, ticker)
            return pd.DataFrame()
        return df
    except Exception as exc:
        logger.warning("Erro ao obter %s para %s: %s", label, ticker, exc)
        return pd.DataFrame()


def extract_key_financials(statements: dict[str, pd.DataFrame]) -> dict:
    """
    Extrai os principais valores financeiros dos demonstrativos para uso nos processors.

    Args:
        statements: Dicionário retornado por get_financial_statements().

    Returns:
        Dicionário com os valores mais recentes de:
        - revenue, net_income, ebitda, gross_profit (DRE)
        - total_assets, total_equity, total_debt, net_debt (Balanço)
        - revenue_history, net_income_history (listas dos últimos 5 anos)
    """
    income = statements.get("income_statement", pd.DataFrame())
    balance = statements.get("balance_sheet", pd.DataFrame())

    def _get_value(df: pd.DataFrame, *keys: str) -> Optional[float]:
        """Tenta obter o valor mais recente de uma linha do DataFrame."""
        if df.empty:
            return None
        for key in keys:
            # Busca case-insensitive
            matches = [idx for idx in df.index if key.lower() in str(idx).lower()]
            if matches:
                row = df.loc[matches[0]]
                # Pega o valor mais recente (primeira coluna)
                val = row.iloc[0] if not row.empty else None
                if val is not None and not pd.isna(val):
                    return float(val)
        return None

    def _get_history(df: pd.DataFrame, *keys: str) -> list[float]:
        """Retorna histórico de valores (últimos 5 anos) para uma linha."""
        if df.empty:
            return []
        for key in keys:
            matches = [idx for idx in df.index if key.lower() in str(idx).lower()]
            if matches:
                row = df.loc[matches[0]]
                values = [float(v) for v in row if v is not None and not pd.isna(v)]
                return values[:5]  # Últimos 5 anos
        return []

    return {
        # DRE
        "revenue": _get_value(income, "Total Revenue", "Net Revenue", "Revenue"),
        "net_income": _get_value(income, "Net Income"),
        "ebitda": _get_value(income, "EBITDA", "Normalized EBITDA"),
        "gross_profit": _get_value(income, "Gross Profit"),
        # Balanço
        "total_assets": _get_value(balance, "Total Assets"),
        "total_equity": _get_value(balance, "Stockholders Equity", "Total Equity"),
        "total_debt": _get_value(balance, "Total Debt", "Long Term Debt"),
        "net_debt": _get_value(balance, "Net Debt"),
        "invested_capital": _get_value(balance, "Invested Capital", "Capital Stock"),
        # Histórico para cálculo de crescimento
        "revenue_history": _get_history(income, "Total Revenue", "Net Revenue", "Revenue"),
        "net_income_history": _get_history(income, "Net Income"),
    }
