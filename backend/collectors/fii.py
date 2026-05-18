"""
Coletor de dados para FIIs (Fundos de Investimento Imobiliário) via yfinance.

Fonte exclusiva: yfinance (fundamentus não suporta FIIs via get_papel).

Indicadores coletados para o MVP:
- Preço atual
- P/VP (Preço / Valor Patrimonial por Cota)
- P/L (Preço / Lucro)
- Dividend Yield anual
- Histórico de dividendos (últimos 12 meses e 5 anos)
- Crescimento de dividendos YoY (CAGR)

Uso:
    from backend.collectors.fii import get_fii_data

    data = get_fii_data("HGLG11")
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

_B3_SUFFIX = ".SA"


def _normalize_ticker(symbol: str) -> str:
    symbol = symbol.upper().strip()
    return symbol if symbol.endswith(_B3_SUFFIX) else symbol + _B3_SUFFIX


def get_fii_data(symbol: str) -> dict:
    """
    Coleta dados completos de um FII via yfinance.

    Args:
        symbol: Símbolo do FII (ex: HGLG11, XPML11).

    Returns:
        Dicionário com todos os dados disponíveis do FII.

    Raises:
        ValueError: Se o FII não for encontrado.
        RuntimeError: Se houver erro na comunicação com a API.

    Exemplo:
        >>> data = get_fii_data("HGLG11")
        >>> print(f"P/VP: {data['pb_ratio']:.2f}")
        P/VP: 0.99
    """
    normalized = _normalize_ticker(symbol)

    try:
        stock = yf.Ticker(normalized)
        info = stock.info

        # Preço atual
        current_price = (
            info.get("regularMarketPrice")
            or info.get("currentPrice")
            or _get_price_from_fast_info(stock)
        )

        if current_price is None:
            raise ValueError(f"FII '{symbol}' não encontrado ou sem cotação disponível.")

        # Dados básicos
        pb_ratio = info.get("priceToBook")
        pe_ratio = info.get("trailingPE")
        market_cap = info.get("marketCap")
        shares_outstanding = info.get("sharesOutstanding")
        book_value_per_share = info.get("bookValue")

        # Dividend Yield
        # yfinance retorna dividendYield em escala variável:
        # - Alguns tickers: decimal (0.0938 = 9.38%) → correto
        # - Outros tickers: percentual (9.38 = 9.38%) → precisa dividir por 100
        # Regra: se valor > 1.0, está em percentual → divide por 100
        dy_raw = info.get("dividendYield")
        if dy_raw is not None:
            dividend_yield = dy_raw / 100 if dy_raw > 1.0 else dy_raw
        else:
            dividend_yield = None

        # Histórico de dividendos
        div_history = _get_dividend_history(stock, symbol)

        # Dividendos últimos 12 meses
        dividends_12m = _sum_dividends_last_n_months(div_history, months=12)

        # Último dividendo
        last_dividend = None
        last_dividend_date = None
        if not div_history.empty:
            last_dividend = float(div_history.iloc[-1])
            last_dividend_date = div_history.index[-1].to_pydatetime()

        # Crescimento de dividendos YoY (CAGR 5 anos)
        dividend_growth_yoy = _calculate_dividend_growth(div_history)

        logger.info(
            "FII %s coletado | Preço: R$%.2f | P/VP: %s | DY: %s%%",
            symbol,
            current_price,
            f"{pb_ratio:.2f}" if pb_ratio else "N/A",
            f"{dividend_yield * 100:.1f}" if dividend_yield else "N/A",
        )

        return {
            "symbol": symbol.upper(),
            "asset_type": "fii",
            # Cotação
            "current_price": current_price,
            "market_cap": market_cap,
            "shares_outstanding": shares_outstanding,
            # Valuation
            "pb_ratio": pb_ratio,
            "pe_ratio": pe_ratio,
            "book_value_per_share": book_value_per_share,
            # Dividendos
            "dividend_yield": dividend_yield,
            "dividends_12m": dividends_12m,
            "last_dividend": last_dividend,
            "last_dividend_date": last_dividend_date,
            "dividend_growth_yoy": dividend_growth_yoy,
            # Histórico bruto (para cálculos futuros)
            "dividend_history": div_history,
        }

    except ValueError:
        raise
    except Exception as exc:
        logger.error("Erro ao coletar FII %s: %s", symbol, exc)
        raise RuntimeError(f"Falha ao coletar dados do FII '{symbol}': {exc}") from exc


def _get_price_from_fast_info(stock: yf.Ticker) -> Optional[float]:
    """Fallback para obter preço via fast_info."""
    try:
        return getattr(stock.fast_info, "last_price", None)
    except Exception:
        return None


def _get_dividend_history(stock: yf.Ticker, symbol: str) -> pd.Series:
    """
    Retorna histórico de dividendos dos últimos 5 anos.

    Returns:
        Series com dividendos indexados por data. Vazio se não disponível.
    """
    try:
        divs = stock.dividends
        if divs is None or divs.empty:
            logger.warning("Sem histórico de dividendos para %s", symbol)
            return pd.Series(dtype=float)

        # Filtra últimos 5 anos
        cutoff = datetime.utcnow() - timedelta(days=5 * 365)
        divs.index = pd.to_datetime(divs.index, utc=True)
        divs = divs[divs.index >= pd.Timestamp(cutoff, tz="UTC")]

        return divs

    except Exception as exc:
        logger.warning("Erro ao obter dividendos de %s: %s", symbol, exc)
        return pd.Series(dtype=float)


def _sum_dividends_last_n_months(div_history: pd.Series, months: int = 12) -> Optional[float]:
    """
    Soma os dividendos pagos nos últimos N meses.

    Args:
        div_history: Série de dividendos históricos.
        months: Número de meses a considerar.

    Returns:
        Soma dos dividendos ou None se sem dados.
    """
    if div_history.empty:
        return None

    cutoff = pd.Timestamp(datetime.utcnow() - timedelta(days=months * 31), tz="UTC")
    recent = div_history[div_history.index >= cutoff]

    if recent.empty:
        return None

    return float(recent.sum())


def _calculate_dividend_growth(div_history: pd.Series) -> Optional[float]:
    """
    Calcula o CAGR dos dividendos anuais nos últimos 5 anos.

    Agrupa dividendos por ano e calcula o crescimento composto.

    Args:
        div_history: Série de dividendos históricos (últimos 5 anos).

    Returns:
        CAGR como decimal (ex: 0.08 = 8% a.a.) ou None se insuficiente.
    """
    if div_history.empty or len(div_history) < 2:
        return None

    try:
        # Agrupa por ano
        annual = div_history.groupby(div_history.index.year).sum()

        if len(annual) < 2:
            return None

        # Remove anos com zero dividendo
        annual = annual[annual > 0]
        if len(annual) < 2:
            return None

        initial = float(annual.iloc[-1])   # Mais antigo
        final = float(annual.iloc[0])      # Mais recente
        n_years = len(annual) - 1

        if initial <= 0 or final <= 0:
            return None

        cagr = (final / initial) ** (1 / n_years) - 1
        return round(cagr, 6)

    except Exception as exc:
        logger.warning("Erro ao calcular crescimento de dividendos: %s", exc)
        return None
