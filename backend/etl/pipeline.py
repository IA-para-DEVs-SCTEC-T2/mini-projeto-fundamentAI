"""
Pipeline de ETL diário do FundamentAI.

Orquestra o fluxo completo:
    Coleta (yfinance + fundamentus + BCB) → Processamento → Persistência

Agendamento: APScheduler, executado diariamente às 19h (horário de Brasília),
após o fechamento do mercado B3 (18h).

Para executar manualmente:
    python -m backend.etl.pipeline

Para iniciar o agendador:
    python -m backend.etl.pipeline --schedule
"""

import argparse
import logging
import sys
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from backend.collectors.bacen import get_macro_context
from backend.collectors.fundamentus import get_fundamentals, get_sector
from backend.collectors.yfinance import (
    extract_key_financials,
    get_financial_statements,
    get_stock_quote,
)
from backend.db.models import SessionLocal, create_tables
from backend.db.repository import FinancialDataRepository, IndicatorsRepository, TickerRepository
from backend.processors.indicators import calculate_all_indicators
from backend.processors.scoring import calculate_score

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lista de tickers monitorados
# ---------------------------------------------------------------------------

# Tickers padrão para o ETL diário.
# Em produção, esta lista pode ser carregada do banco de dados.
DEFAULT_TICKERS = [
    # Petróleo e Gás
    "PETR4", "PETR3", "PRIO3",
    # Mineração
    "VALE3",
    # Financeiro
    "ITUB4", "BBDC4", "BBAS3", "SANB11",
    # Energia Elétrica
    "EGIE3", "TAEE11", "ENGI11",
    # Varejo
    "MGLU3", "VIIA3", "LREN3",
    # Saúde
    "RDOR3", "HAPV3",
    # Tecnologia
    "TOTVS3",
    # Telecomunicações
    "VIVT3",
    # Consumo
    "ABEV3", "JBSS3",
]

# Configurações de retry
_MAX_RETRIES = 3
_RETRY_DELAY_SECONDS = 5


# ---------------------------------------------------------------------------
# Funções do pipeline
# ---------------------------------------------------------------------------


def run_etl_for_ticker(
    ticker: str,
    db: Session,
    macro_context: Optional[dict] = None,
) -> dict:
    """
    Executa o ETL completo para um único ticker.

    Fluxo: Coleta → Processamento → Persistência

    Args:
        ticker: Símbolo do ativo (ex: PETR4).
        db: Sessão do banco de dados.
        macro_context: Contexto macroeconômico pré-coletado (reutilizado entre tickers).

    Returns:
        Dicionário com resultado do ETL:
        - ticker: Símbolo
        - status: "success" | "error" | "partial"
        - indicators: Indicadores calculados (se sucesso)
        - score: Score calculado (se sucesso)
        - error: Mensagem de erro (se falha)
    """
    logger.info("[ETL] Processando ticker: %s", ticker)
    result: dict = {"ticker": ticker, "status": "error"}

    # --- Coleta ---
    try:
        quote = get_stock_quote(ticker)
    except (ValueError, RuntimeError) as exc:
        logger.error("[ETL] Falha ao coletar cotação de %s: %s", ticker, exc)
        result["error"] = f"Cotação indisponível: {exc}"
        return result

    try:
        statements = get_financial_statements(ticker)
        financial_data = extract_key_financials(statements)
        financial_data["current_price"] = quote.get("current_price")
    except RuntimeError as exc:
        logger.warning("[ETL] Demonstrativos indisponíveis para %s: %s", ticker, exc)
        financial_data = {"current_price": quote.get("current_price")}
        result["status"] = "partial"

    fundamentus_data = None
    sector = None
    try:
        fundamentus_data = get_fundamentals(ticker)
        sector = get_sector(ticker)
    except (ValueError, RuntimeError) as exc:
        logger.warning("[ETL] Fundamentus indisponível para %s: %s", ticker, exc)

    # --- Processamento ---
    indicators = calculate_all_indicators(financial_data, quote, fundamentus_data)
    score_result = calculate_score(indicators)

    # --- Persistência ---
    try:
        _persist_to_db(db, ticker, quote, financial_data, indicators, score_result, sector)
    except Exception as exc:
        logger.error("[ETL] Falha ao persistir dados de %s: %s", ticker, exc)
        result["error"] = f"Falha na persistência: {exc}"
        return result

    result.update({
        "status": result.get("status") or "success",
        "indicators": indicators,
        "score": score_result["score"],
        "score_label": score_result["label"],
        "sector": sector,
    })

    logger.info(
        "[ETL] %s concluído | Score: %.1f (%s) | Status: %s",
        ticker,
        score_result["score"],
        score_result["label"],
        result["status"],
    )

    return result


def run_full_pipeline(
    tickers: Optional[list[str]] = None,
    stop_on_error: bool = False,
) -> dict:
    """
    Executa o pipeline ETL completo para todos os tickers monitorados.

    Args:
        tickers: Lista de tickers a processar. Se None, usa DEFAULT_TICKERS.
        stop_on_error: Se True, interrompe ao primeiro erro. Padrão: False.

    Returns:
        Relatório de execução com:
        - started_at: Timestamp de início
        - finished_at: Timestamp de fim
        - duration_seconds: Duração total
        - total: Total de tickers processados
        - success: Tickers processados com sucesso
        - partial: Tickers com dados parciais
        - errors: Tickers com falha
        - results: Lista detalhada por ticker
    """
    tickers = tickers or DEFAULT_TICKERS
    started_at = datetime.utcnow()

    logger.info(
        "[ETL] Iniciando pipeline | %d tickers | %s",
        len(tickers),
        started_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
    )

    # Coleta contexto macro uma vez (reutilizado para todos os tickers)
    macro_context = None
    try:
        macro_context = get_macro_context()
        logger.info(
            "[ETL] Contexto macro coletado | SELIC: %s%% | IPCA 12m: %s%%",
            macro_context.get("selic_rate", "N/A"),
            macro_context.get("ipca_12m", "N/A"),
        )
    except Exception as exc:
        logger.warning("[ETL] Falha ao coletar contexto macro: %s", exc)

    results = []
    success_count = 0
    partial_count = 0
    error_count = 0

    db = SessionLocal()
    try:
        for ticker in tickers:
            try:
                result = run_etl_for_ticker(ticker, db, macro_context)
                results.append(result)

                if result["status"] == "success":
                    success_count += 1
                elif result["status"] == "partial":
                    partial_count += 1
                else:
                    error_count += 1
                    if stop_on_error:
                        logger.error("[ETL] Interrompendo por erro em %s", ticker)
                        break

            except Exception as exc:
                logger.error("[ETL] Erro inesperado ao processar %s: %s", ticker, exc)
                results.append({"ticker": ticker, "status": "error", "error": str(exc)})
                error_count += 1
                if stop_on_error:
                    break

    finally:
        db.close()

    finished_at = datetime.utcnow()
    duration = (finished_at - started_at).total_seconds()

    report = {
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "duration_seconds": round(duration, 2),
        "total": len(tickers),
        "success": success_count,
        "partial": partial_count,
        "errors": error_count,
        "results": results,
    }

    logger.info(
        "[ETL] Pipeline concluído em %.1fs | Sucesso: %d | Parcial: %d | Erros: %d",
        duration,
        success_count,
        partial_count,
        error_count,
    )

    return report


def _persist_to_db(
    db: Session,
    ticker: str,
    quote: dict,
    financial_data: dict,
    indicators: dict,
    score_result: dict,
    sector: Optional[str],
) -> None:
    """Persiste todos os dados processados no banco de dados."""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    ticker_repo = TickerRepository(db)
    financial_repo = FinancialDataRepository(db)
    indicators_repo = IndicatorsRepository(db)

    db_ticker, created = ticker_repo.get_or_create(ticker, sector=sector)
    if created:
        logger.info("[ETL] Novo ticker cadastrado: %s", ticker)

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
        score=score_result.get("score"),
        score_label=score_result.get("label"),
        **{k: v for k, v in indicators.items() if v is not None},
    )


# ---------------------------------------------------------------------------
# Agendador (APScheduler)
# ---------------------------------------------------------------------------


def start_scheduler(hour: int = 19, minute: int = 0) -> None:
    """
    Inicia o agendador APScheduler para execução diária do ETL.

    O mercado B3 fecha às 18h (horário de Brasília). O ETL é agendado
    para 19h para garantir que todos os dados do dia estejam disponíveis.

    Args:
        hour: Hora de execução (padrão: 19).
        minute: Minuto de execução (padrão: 0).
    """
    try:
        from apscheduler.schedulers.blocking import BlockingScheduler
        from apscheduler.triggers.cron import CronTrigger
    except ImportError:
        logger.error(
            "APScheduler não instalado. Execute: pip install apscheduler"
        )
        sys.exit(1)

    scheduler = BlockingScheduler(timezone="America/Sao_Paulo")

    scheduler.add_job(
        func=run_full_pipeline,
        trigger=CronTrigger(hour=hour, minute=minute, timezone="America/Sao_Paulo"),
        id="daily_etl",
        name="ETL Diário FundamentAI",
        replace_existing=True,
    )

    logger.info(
        "[ETL] Agendador iniciado | Execução diária às %02d:%02d (Brasília)",
        hour,
        minute,
    )

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("[ETL] Agendador encerrado")
        scheduler.shutdown()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    parser = argparse.ArgumentParser(description="FundamentAI ETL Pipeline")
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Inicia o agendador para execução diária automática",
    )
    parser.add_argument(
        "--tickers",
        nargs="+",
        help="Lista de tickers específicos para processar (ex: PETR4 VALE3)",
    )
    parser.add_argument(
        "--hour",
        type=int,
        default=19,
        help="Hora de execução do agendador (padrão: 19)",
    )
    parser.add_argument(
        "--minute",
        type=int,
        default=0,
        help="Minuto de execução do agendador (padrão: 0)",
    )
    args = parser.parse_args()

    # Garante que as tabelas existem
    create_tables()

    if args.schedule:
        start_scheduler(hour=args.hour, minute=args.minute)
    else:
        # Execução manual imediata
        report = run_full_pipeline(tickers=args.tickers)
        print(f"\n{'='*50}")
        print(f"ETL concluído em {report['duration_seconds']}s")
        print(f"Sucesso: {report['success']} | Parcial: {report['partial']} | Erros: {report['errors']}")
        print(f"{'='*50}")
