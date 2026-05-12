"""
Endpoint de consulta por ticker.

GET /api/ticker/{ticker}
Retorna dados financeiros, indicadores e histórico de preços de um ativo da B3.
Suporta ações (via fundamentus + yfinance) e FIIs (via yfinance).
"""

import logging
import re
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.collectors.fii import get_fii_data
from backend.collectors.fundamentus import get_fundamentals, get_sector
from backend.collectors.yfinance import (
    extract_key_financials,
    get_financial_statements,
    get_price_history,
    get_stock_quote,
)
from backend.db.models import ASSET_TYPE_FII, ASSET_TYPE_STOCK, get_db
from backend.db.repository import FinancialDataRepository, IndicatorsRepository, TickerRepository
from backend.processors.asset_classifier import classify_asset_type, get_inactive_symbols
from backend.processors.indicators import calculate_all_indicators, calculate_fii_indicators
from backend.processors.scoring import calculate_score

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ticker", tags=["ticker"])

# Regex para validar formato de ticker da B3
_TICKER_PATTERN = re.compile(r"^[A-Z]{4}\d{1,2}(F)?$")


# ---------------------------------------------------------------------------
# Schemas de resposta (unificados para ações e FIIs)
# ---------------------------------------------------------------------------


class QuoteResponse(BaseModel):
    ticker: str
    current_price: Optional[float] = None
    previous_close: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[float] = None
    market_cap: Optional[float] = None
    currency: str = "BRL"


class IndicatorsResponse(BaseModel):
    # Comuns
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    # Ações
    roe: Optional[float] = None
    roic: Optional[float] = None
    net_margin: Optional[float] = None
    debt_ebitda: Optional[float] = None
    ev_ebitda: Optional[float] = None
    net_income_growth_yoy: Optional[float] = None
    revenue_growth_yoy: Optional[float] = None
    # FIIs
    dividend_growth_yoy: Optional[float] = None


class ScoreResponse(BaseModel):
    score: float
    label: str
    asset_type: str


class PricePoint(BaseModel):
    date: str
    close: float
    volume: Optional[float] = None


class TickerResponse(BaseModel):
    ticker: str
    name: Optional[str] = None
    sector: Optional[str] = None
    asset_type: str  # "stock" | "fii"
    quote: QuoteResponse
    indicators: IndicatorsResponse
    score: ScoreResponse
    price_history: list[PricePoint]
    data_source: str


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.get(
    "/{ticker}",
    response_model=TickerResponse,
    summary="Consulta dados de um ativo da B3",
    description=(
        "Retorna cotação, indicadores fundamentalistas, score e histórico de preços. "
        "Ações: dados via fundamentus + yfinance. FIIs: dados via yfinance."
    ),
)
def get_ticker_data(
    ticker: str,
    history_years: int = Query(default=5, ge=1, le=10, description="Anos de histórico"),
    db: Session = Depends(get_db),
) -> TickerResponse:
    """
    Consulta dados completos de um ativo da B3.

    Raises:
        400: Formato de ticker inválido.
        404: Ticker não encontrado, inativo ou sem dados.
        500: Erro interno.
    """
    ticker = ticker.upper().strip()

    # Valida formato
    if not _TICKER_PATTERN.match(ticker):
        raise HTTPException(
            status_code=400,
            detail=f"Formato de ticker inválido: '{ticker}'. Use o padrão da B3 (ex: PETR4, HGLG11).",
        )

    # Verifica se é inativo
    inactive = get_inactive_symbols(db)
    if ticker in inactive:
        raise HTTPException(
            status_code=404,
            detail={
                "message": f"O ativo '{ticker}' não está disponível para consulta.",
                "reason": "inactive",
                "description": (
                    "Este ticker está classificado como inativo na B3 — "
                    "sem cotação de mercado ou dados financeiros disponíveis. "
                    "Consulte apenas ativos ativamente negociados."
                ),
            },
        )

    asset_type = classify_asset_type(ticker)
    logger.info("Consultando %s (tipo: %s)", ticker, asset_type)

    if asset_type == ASSET_TYPE_FII:
        return _get_fii_data(ticker, history_years, db)
    return _get_stock_data(ticker, history_years, db)


# ---------------------------------------------------------------------------
# Handlers por tipo de ativo
# ---------------------------------------------------------------------------


def _get_stock_data(ticker: str, history_years: int, db: Session) -> TickerResponse:
    """Coleta e processa dados de uma AÇÃO."""

    # Cotação
    try:
        quote = get_stock_quote(ticker)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao coletar cotação: {exc}")

    # Demonstrativos financeiros
    try:
        statements = get_financial_statements(ticker)
        financial_data = extract_key_financials(statements)
        financial_data["current_price"] = quote.get("current_price")
    except RuntimeError:
        financial_data = {"current_price": quote.get("current_price")}

    # Fundamentus
    fundamentus_data = None
    sector = None
    name = None
    try:
        fundamentus_data = get_fundamentals(ticker)
        sector = get_sector(ticker)
        name = fundamentus_data.get("name") if fundamentus_data else None
    except (ValueError, RuntimeError):
        pass

    # Histórico de preços
    price_history_df = None
    try:
        price_history_df = get_price_history(ticker, years=history_years)
    except RuntimeError:
        pass

    # Indicadores
    indicators = calculate_all_indicators(financial_data, quote, fundamentus_data)
    score_result = calculate_score(indicators, asset_type=ASSET_TYPE_STOCK)

    # Persiste
    _persist_data(db, ticker, ASSET_TYPE_STOCK, quote, financial_data, indicators, score_result, sector)

    return TickerResponse(
        ticker=ticker,
        name=name,
        sector=sector,
        asset_type=ASSET_TYPE_STOCK,
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
        score=ScoreResponse(
            score=score_result["score"],
            label=score_result["label"],
            asset_type=ASSET_TYPE_STOCK,
        ),
        price_history=_build_price_history(price_history_df),
        data_source="fundamentus + yfinance",
    )


def _get_fii_data(ticker: str, history_years: int, db: Session) -> TickerResponse:
    """Coleta e processa dados de um FII."""

    try:
        fii_data = get_fii_data(ticker)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao coletar dados do FII: {exc}")

    # Histórico de preços
    price_history_df = None
    try:
        price_history_df = get_price_history(ticker, years=history_years)
    except RuntimeError:
        pass

    indicators = calculate_fii_indicators(fii_data)
    score_result = calculate_score(indicators, asset_type=ASSET_TYPE_FII)

    # Persiste
    quote = {
        "current_price": fii_data.get("current_price"),
        "market_cap": fii_data.get("market_cap"),
    }
    _persist_data(db, ticker, ASSET_TYPE_FII, quote, fii_data, indicators, score_result, sector=None)

    return TickerResponse(
        ticker=ticker,
        name=None,
        sector="Fundos Imobiliários",
        asset_type=ASSET_TYPE_FII,
        quote=QuoteResponse(
            ticker=ticker,
            current_price=fii_data.get("current_price"),
            market_cap=fii_data.get("market_cap"),
        ),
        indicators=IndicatorsResponse(**{
            k: indicators.get(k) for k in IndicatorsResponse.model_fields
        }),
        score=ScoreResponse(
            score=score_result["score"],
            label=score_result["label"],
            asset_type=ASSET_TYPE_FII,
        ),
        price_history=_build_price_history(price_history_df),
        data_source="yfinance",
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_price_history(df) -> list[PricePoint]:
    if df is None or df.empty:
        return []
    result = []
    for date, row in df.iterrows():
        result.append(PricePoint(
            date=str(date.date()),
            close=round(float(row["Close"]), 2),
            volume=float(row["Volume"]) if row.get("Volume") else None,
        ))
    return result


def _persist_data(
    db: Session,
    ticker: str,
    asset_type: str,
    quote: dict,
    financial_data: dict,
    indicators: dict,
    score_result: dict,
    sector: Optional[str],
) -> None:
    """Persiste dados coletados no banco (upsert, best-effort)."""
    try:
        ticker_repo = TickerRepository(db)
        financial_repo = FinancialDataRepository(db)
        indicators_repo = IndicatorsRepository(db)

        db_ticker, _ = ticker_repo.get_or_create(ticker, sector=sector, asset_type=asset_type)
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        fin_kwargs = {
            "current_price": quote.get("current_price"),
            "market_cap": quote.get("market_cap"),
        }
        if asset_type == ASSET_TYPE_STOCK:
            fin_kwargs.update({
                "revenue": financial_data.get("revenue"),
                "net_income": financial_data.get("net_income"),
                "total_equity": financial_data.get("total_equity"),
                "total_debt": financial_data.get("total_debt"),
                "net_debt": financial_data.get("net_debt"),
            })
        else:
            fin_kwargs.update({
                "book_value_per_share": financial_data.get("book_value_per_share"),
                "dividend_yield": financial_data.get("dividend_yield"),
                "dividends_12m": financial_data.get("dividends_12m"),
                "last_dividend": financial_data.get("last_dividend"),
                "last_dividend_date": financial_data.get("last_dividend_date"),
                "dividend_growth_yoy": financial_data.get("dividend_growth_yoy"),
            })

        financial_repo.upsert(ticker_id=db_ticker.id, reference_date=today,
                              **{k: v for k, v in fin_kwargs.items() if v is not None})

        valid_fields = {
            "roe", "roic", "net_margin", "debt_ebitda", "ev_ebitda",
            "pe_ratio", "pb_ratio", "dividend_yield", "dividend_growth_yoy",
            "revenue_growth_yoy", "net_income_growth_yoy",
        }
        ind_kwargs = {k: v for k, v in indicators.items() if k in valid_fields and v is not None}
        indicators_repo.upsert(
            ticker_id=db_ticker.id, reference_date=today,
            score=score_result["score"], score_label=score_result["label"],
            **ind_kwargs,
        )

    except Exception as exc:
        logger.warning("Falha ao persistir %s: %s", ticker, exc)
