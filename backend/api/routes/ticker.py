"""
Endpoint de consulta por ticker.

GET /api/ticker/{ticker}
Retorna dados financeiros, indicadores e histórico de preços de um ativo da B3.
"""

import logging
import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.collectors.fundamentus import get_fundamentals, get_sector
from backend.collectors.yfinance import (
    extract_key_financials,
    get_financial_statements,
    get_price_history,
    get_stock_quote,
)
from backend.db.models import get_db
from backend.db.repository import FinancialDataRepository, IndicatorsRepository, TickerRepository
from backend.processors.indicators import calculate_all_indicators

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ticker", tags=["ticker"])

# Regex para validar formato de ticker da B3 (ex: PETR4, VALE3, HGLG11)
_TICKER_PATTERN = re.compile(r"^[A-Z]{4}\d{1,2}(F)?$")


# ---------------------------------------------------------------------------
# Schemas de resposta
# ---------------------------------------------------------------------------


class QuoteResponse(BaseModel):
    ticker: str
    current_price: Optional[float]
    previous_close: Optional[float]
    change_percent: Optional[float]
    volume: Optional[float]
    market_cap: Optional[float]
    currency: str = "BRL"


class IndicatorsResponse(BaseModel):
    roe: Optional[float]
    roic: Optional[float]
    net_margin: Optional[float]
    debt_ebitda: Optional[float]
    pe_ratio: Optional[float]
    pb_ratio: Optional[float]
    revenue_growth_yoy: Optional[float]
    net_income_growth_yoy: Optional[float]


class PricePoint(BaseModel):
    date: str
    close: float
    volume: Optional[float]


class TickerResponse(BaseModel):
    ticker: str
    name: Optional[str]
    sector: Optional[str]
    quote: QuoteResponse
    indicators: IndicatorsResponse
    price_history: list[PricePoint]
    data_source: str = "yfinance + fundamentus"


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.get(
    "/{ticker}",
    response_model=TickerResponse,
    summary="Consulta dados de um ativo da B3",
    description=(
        "Retorna cotação atual, indicadores fundamentalistas e histórico de preços "
        "para um ativo da B3. Dados coletados via yfinance e fundamentus."
    ),
)
def get_ticker_data(
    ticker: str,
    history_years: int = Query(default=5, ge=1, le=10, description="Anos de histórico de preços"),
    db: Session = Depends(get_db),
) -> TickerResponse:
    """
    Consulta dados completos de um ativo da B3.

    Args:
        ticker: Símbolo do ativo (ex: PETR4, VALE3, HGLG11).
        history_years: Número de anos de histórico de preços (1-10, padrão: 5).

    Returns:
        Dados completos do ativo incluindo cotação, indicadores e histórico.

    Raises:
        400: Formato de ticker inválido.
        404: Ticker não encontrado ou sem dados disponíveis.
        500: Erro interno ao coletar dados.

    Exemplo:
        GET /api/ticker/PETR4
        GET /api/ticker/VALE3?history_years=3
    """
    ticker = ticker.upper().strip()

    # Valida formato do ticker
    if not _TICKER_PATTERN.match(ticker):
        raise HTTPException(
            status_code=400,
            detail=f"Formato de ticker inválido: '{ticker}'. Use o formato padrão da B3 (ex: PETR4, VALE3).",
        )

    logger.info("Consultando dados para ticker: %s", ticker)

    # --- Coleta de dados ---
    try:
        quote = get_stock_quote(ticker)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except RuntimeError as exc:
        logger.error("Erro ao coletar cotação de %s: %s", ticker, exc)
        raise HTTPException(status_code=500, detail=f"Erro ao coletar cotação: {exc}")

    # Demonstrativos financeiros
    try:
        statements = get_financial_statements(ticker)
        financial_data = extract_key_financials(statements)
        financial_data["current_price"] = quote.get("current_price")
    except RuntimeError as exc:
        logger.warning("Erro ao coletar demonstrativos de %s: %s", ticker, exc)
        financial_data = {"current_price": quote.get("current_price")}

    # Indicadores do fundamentus (melhor fonte para B3)
    fundamentus_data = None
    sector = None
    try:
        fundamentus_data = get_fundamentals(ticker)
        sector = get_sector(ticker)
    except (ValueError, RuntimeError) as exc:
        logger.warning("Fundamentus indisponível para %s: %s", ticker, exc)

    # Histórico de preços
    price_history_df = None
    try:
        price_history_df = get_price_history(ticker, years=history_years)
    except RuntimeError as exc:
        logger.warning("Erro ao coletar histórico de %s: %s", ticker, exc)

    # --- Processamento ---
    indicators = calculate_all_indicators(financial_data, quote, fundamentus_data)

    # --- Persistência (upsert no banco) ---
    _persist_ticker_data(db, ticker, quote, financial_data, indicators, sector)

    # --- Monta resposta ---
    price_history = []
    if price_history_df is not None and not price_history_df.empty:
        for date, row in price_history_df.iterrows():
            price_history.append(
                PricePoint(
                    date=str(date.date()),
                    close=round(float(row["Close"]), 2),
                    volume=float(row["Volume"]) if row["Volume"] else None,
                )
            )

    return TickerResponse(
        ticker=ticker,
        name=fundamentus_data.get("name") if fundamentus_data else None,
        sector=sector,
        quote=QuoteResponse(
            ticker=ticker,
            current_price=quote.get("current_price"),
            previous_close=quote.get("previous_close"),
            change_percent=quote.get("change_percent"),
            volume=quote.get("volume"),
            market_cap=quote.get("market_cap"),
        ),
        indicators=IndicatorsResponse(**{
            k: indicators.get(k) for k in IndicatorsResponse.model_fields
        }),
        price_history=price_history,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _persist_ticker_data(
    db: Session,
    ticker: str,
    quote: dict,
    financial_data: dict,
    indicators: dict,
    sector: Optional[str],
) -> None:
    """Persiste os dados coletados no banco de dados (upsert)."""
    from datetime import datetime

    try:
        ticker_repo = TickerRepository(db)
        financial_repo = FinancialDataRepository(db)
        indicators_repo = IndicatorsRepository(db)

        db_ticker, _ = ticker_repo.get_or_create(ticker, sector=sector)

        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        financial_repo.upsert(
            ticker_id=db_ticker.id,
            reference_date=today,
            current_price=quote.get("current_price"),
            market_cap=quote.get("market_cap"),
            revenue=financial_data.get("revenue"),
            net_income=financial_data.get("net_income"),
            ebitda=financial_data.get("ebitda"),
            total_equity=financial_data.get("total_equity"),
            total_debt=financial_data.get("total_debt"),
            net_debt=financial_data.get("net_debt"),
        )

        indicators_repo.upsert(
            ticker_id=db_ticker.id,
            reference_date=today,
            **{k: v for k, v in indicators.items() if v is not None},
        )

    except Exception as exc:
        logger.warning("Falha ao persistir dados de %s: %s", ticker, exc)
        # Não propaga o erro — persistência é best-effort
