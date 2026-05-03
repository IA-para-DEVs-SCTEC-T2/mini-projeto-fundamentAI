"""
Endpoint de análise e veredito via Anthropic API.

POST /api/analysis/{ticker}
Gera análise estruturada de um ativo usando Claude (Sonnet ou Haiku),
retornando veredito, score, pontos positivos/negativos e explicações.
"""

import json
import logging
import os
from typing import Literal, Optional

import anthropic
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.collectors.bacen import get_macro_context
from backend.collectors.fundamentus import get_fundamentals, get_sector
from backend.collectors.yfinance import (
    extract_key_financials,
    get_financial_statements,
    get_stock_quote,
)
from backend.db.models import get_db
from backend.db.repository import AnalysisRepository, TickerRepository
from backend.processors.comparator import (
    calculate_sector_averages,
    compare_to_sector,
    get_sector_companies,
)
from backend.processors.indicators import calculate_all_indicators
from backend.processors.scoring import calculate_score
from backend.prompts.builder import PROMPT_VERSION, build_analysis_prompt, parse_llm_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

# Modelos disponíveis
_MODEL_SONNET = "claude-sonnet-4-5"
_MODEL_HAIKU = "claude-haiku-4-5"

# Timeout para chamadas à Anthropic API (segundos)
_ANTHROPIC_TIMEOUT = 60.0

# Máximo de tokens na resposta
_MAX_TOKENS = 2048


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class AnalysisRequest(BaseModel):
    model: Literal["sonnet", "haiku"] = "sonnet"
    use_cache: bool = True


class IndicatorsExplanation(BaseModel):
    roe: Optional[str] = None
    roic: Optional[str] = None
    net_margin: Optional[str] = None
    debt_ebitda: Optional[str] = None
    pe_ratio: Optional[str] = None
    pb_ratio: Optional[str] = None
    growth: Optional[str] = None


class AnalysisResponse(BaseModel):
    ticker: str
    verdict: str
    score: float
    confidence_level: str
    positive_points: list[str]
    negative_points: list[str]
    indicators_explanation: IndicatorsExplanation
    moment_suggestion: Optional[str] = None
    conclusion: str
    risk_assessment: Optional[str] = None
    disclaimer: str
    model_used: str
    prompt_version: str
    cached: bool = False


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.post(
    "/{ticker}",
    response_model=AnalysisResponse,
    summary="Gera análise fundamentalista de um ativo",
    description=(
        "Coleta dados do ativo, calcula indicadores, monta prompt estruturado "
        "e envia à Anthropic API (Claude) para geração de análise completa. "
        "Retorna veredito, score, pontos positivos/negativos e explicações educativas."
    ),
)
def generate_analysis(
    ticker: str,
    request: AnalysisRequest = None,
    db: Session = Depends(get_db),
) -> AnalysisResponse:
    """
    Gera análise fundamentalista completa de um ativo da B3.

    Args:
        ticker: Símbolo do ativo (ex: PETR4, VALE3).
        request: Configurações da análise (modelo, cache).

    Returns:
        Análise estruturada com veredito, score, explicações e conclusão.

    Raises:
        400: Ticker inválido.
        404: Ticker não encontrado.
        503: Anthropic API indisponível.
        500: Erro interno.
    """
    if request is None:
        request = AnalysisRequest()

    ticker = ticker.upper().strip()
    logger.info("Gerando análise para %s (modelo: %s)", ticker, request.model)

    # --- Verifica cache ---
    if request.use_cache:
        cached = _get_cached_analysis(db, ticker)
        if cached:
            logger.info("Retornando análise em cache para %s", ticker)
            return cached

    # --- Coleta de dados ---
    financial_data, quote, fundamentus_data, sector = _collect_data(ticker)
    macro = _collect_macro()

    # --- Processamento ---
    indicators = calculate_all_indicators(financial_data, quote, fundamentus_data)
    score_result = calculate_score(indicators)

    # Comparação setorial (best-effort)
    sector_comparison = None
    if sector:
        try:
            companies = get_sector_companies(sector)
            if not companies.empty:
                averages = calculate_sector_averages(companies)
                sector_comparison = compare_to_sector(ticker, indicators, sector, averages)
        except Exception as exc:
            logger.warning("Comparação setorial falhou para %s: %s", ticker, exc)

    # --- Monta prompt ---
    prompt_data = build_analysis_prompt(
        ticker=ticker,
        financial_data=financial_data,
        indicators=indicators,
        macro=macro,
        score_result=score_result,
        sector_comparison=sector_comparison,
        sector=sector,
    )

    # --- Chama Anthropic API ---
    model_name = _MODEL_SONNET if request.model == "sonnet" else _MODEL_HAIKU
    raw_response = _call_anthropic(
        system_prompt=prompt_data["system_prompt"],
        user_prompt=prompt_data["user_prompt"],
        model=model_name,
    )

    # --- Parseia resposta ---
    try:
        parsed = parse_llm_response(raw_response)
    except ValueError as exc:
        logger.error("Falha ao parsear resposta da LLM para %s: %s", ticker, exc)
        raise HTTPException(
            status_code=500,
            detail=f"Resposta da LLM em formato inválido: {exc}",
        )

    # --- Persiste análise ---
    _persist_analysis(db, ticker, parsed, model_name, raw_response)

    return AnalysisResponse(
        ticker=ticker,
        verdict=parsed.get("verdict", "Neutro"),
        score=float(parsed.get("score", score_result["score"])),
        confidence_level=parsed.get("confidence_level", "Médio"),
        positive_points=parsed.get("positive_points", []),
        negative_points=parsed.get("negative_points", []),
        indicators_explanation=IndicatorsExplanation(
            **{
                k: v
                for k, v in parsed.get("indicators_explanation", {}).items()
                if k in IndicatorsExplanation.model_fields
            }
        ),
        moment_suggestion=parsed.get("moment_suggestion"),
        conclusion=parsed.get("conclusion", ""),
        risk_assessment=parsed.get("risk_assessment"),
        disclaimer=parsed.get(
            "disclaimer",
            "Esta análise é informativa e baseada em dados históricos. "
            "Não constitui recomendação de investimento.",
        ),
        model_used=model_name,
        prompt_version=PROMPT_VERSION,
        cached=False,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _collect_data(ticker: str) -> tuple[dict, dict, Optional[dict], Optional[str]]:
    """
    Coleta todos os dados necessários para a análise.

    Returns:
        (financial_data, quote, fundamentus_data, sector)
    """
    # Cotação
    try:
        quote = get_stock_quote(ticker)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao coletar cotação: {exc}")

    # Demonstrativos
    try:
        statements = get_financial_statements(ticker)
        financial_data = extract_key_financials(statements)
        financial_data["current_price"] = quote.get("current_price")
    except RuntimeError as exc:
        logger.warning("Demonstrativos indisponíveis para %s: %s", ticker, exc)
        financial_data = {"current_price": quote.get("current_price")}

    # Fundamentus
    fundamentus_data = None
    sector = None
    try:
        fundamentus_data = get_fundamentals(ticker)
        sector = get_sector(ticker)
    except (ValueError, RuntimeError) as exc:
        logger.warning("Fundamentus indisponível para %s: %s", ticker, exc)

    return financial_data, quote, fundamentus_data, sector


def _collect_macro() -> dict:
    """Coleta contexto macroeconômico com fallback."""
    try:
        return get_macro_context()
    except Exception as exc:
        logger.warning("Falha ao coletar dados macro: %s", exc)
        return {}


def _call_anthropic(system_prompt: str, user_prompt: str, model: str) -> str:
    """
    Chama a Anthropic API e retorna a resposta bruta.

    Args:
        system_prompt: Prompt de sistema.
        user_prompt: Prompt do usuário com dados injetados.
        model: Nome do modelo Claude a usar.

    Returns:
        Texto da resposta da LLM.

    Raises:
        HTTPException 503: Se a API estiver indisponível.
        HTTPException 500: Para outros erros.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="ANTHROPIC_API_KEY não configurada. Verifique as variáveis de ambiente.",
        )

    try:
        client = anthropic.Anthropic(api_key=api_key)

        message = client.messages.create(
            model=model,
            max_tokens=_MAX_TOKENS,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            timeout=_ANTHROPIC_TIMEOUT,
        )

        response_text = message.content[0].text
        logger.info(
            "Resposta da Anthropic recebida | modelo: %s | tokens: %d",
            model,
            message.usage.output_tokens,
        )
        return response_text

    except anthropic.APITimeoutError:
        logger.error("Timeout na Anthropic API para modelo %s", model)
        raise HTTPException(
            status_code=503,
            detail="Timeout na API de análise. Tente novamente em alguns instantes.",
        )
    except anthropic.APIConnectionError as exc:
        logger.error("Erro de conexão com Anthropic API: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="Serviço de análise temporariamente indisponível.",
        )
    except anthropic.AuthenticationError:
        logger.error("Chave da Anthropic API inválida")
        raise HTTPException(
            status_code=500,
            detail="Configuração inválida do serviço de análise.",
        )
    except anthropic.RateLimitError:
        logger.warning("Rate limit atingido na Anthropic API")
        raise HTTPException(
            status_code=503,
            detail="Limite de requisições atingido. Tente novamente em alguns instantes.",
        )
    except Exception as exc:
        logger.error("Erro inesperado na Anthropic API: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar análise: {exc}",
        )


def _get_cached_analysis(db: Session, ticker: str) -> Optional[AnalysisResponse]:
    """
    Verifica se existe análise recente em cache (gerada hoje).

    Returns:
        AnalysisResponse se cache válido, None caso contrário.
    """
    from datetime import datetime, timedelta

    try:
        ticker_repo = TickerRepository(db)
        db_ticker = ticker_repo.get_by_symbol(ticker)
        if not db_ticker:
            return None

        analysis_repo = AnalysisRepository(db)
        latest = analysis_repo.get_latest(db_ticker.id)

        if not latest:
            return None

        # Cache válido por 24 horas
        cache_ttl = timedelta(hours=24)
        if datetime.utcnow() - latest.generated_at > cache_ttl:
            return None

        # Reconstrói resposta do cache
        positive_points = json.loads(latest.positive_points or "[]")
        negative_points = json.loads(latest.negative_points or "[]")
        indicators_exp = json.loads(latest.indicators_explanation or "{}")

        return AnalysisResponse(
            ticker=ticker,
            verdict=latest.verdict or "Neutro",
            score=latest.score or 0.0,
            confidence_level=latest.confidence_level or "Médio",
            positive_points=positive_points,
            negative_points=negative_points,
            indicators_explanation=IndicatorsExplanation(**{
                k: v for k, v in indicators_exp.items()
                if k in IndicatorsExplanation.model_fields
            }),
            moment_suggestion=latest.moment_suggestion,
            conclusion=latest.conclusion or "",
            risk_assessment=None,
            disclaimer=(
                "Esta análise é informativa e baseada em dados históricos. "
                "Não constitui recomendação de investimento."
            ),
            model_used=latest.model_used or _MODEL_SONNET,
            prompt_version=latest.prompt_version or PROMPT_VERSION,
            cached=True,
        )

    except Exception as exc:
        logger.warning("Erro ao verificar cache para %s: %s", ticker, exc)
        return None


def _persist_analysis(
    db: Session,
    ticker: str,
    parsed: dict,
    model_name: str,
    raw_response: str,
) -> None:
    """Persiste a análise gerada no banco de dados."""
    try:
        ticker_repo = TickerRepository(db)
        db_ticker, _ = ticker_repo.get_or_create(ticker)

        analysis_repo = AnalysisRepository(db)
        analysis_repo.create(
            ticker_id=db_ticker.id,
            verdict=parsed.get("verdict"),
            score=parsed.get("score"),
            confidence_level=parsed.get("confidence_level"),
            positive_points=json.dumps(parsed.get("positive_points", []), ensure_ascii=False),
            negative_points=json.dumps(parsed.get("negative_points", []), ensure_ascii=False),
            indicators_explanation=json.dumps(
                parsed.get("indicators_explanation", {}), ensure_ascii=False
            ),
            conclusion=parsed.get("conclusion"),
            moment_suggestion=parsed.get("moment_suggestion"),
            model_used=model_name,
            prompt_version=PROMPT_VERSION,
            raw_response=raw_response,
        )

    except Exception as exc:
        logger.warning("Falha ao persistir análise de %s: %s", ticker, exc)
