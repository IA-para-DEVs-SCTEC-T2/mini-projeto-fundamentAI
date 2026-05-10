"""
Script para atualizar net_income_growth_yoy e revenue_growth_yoy no banco.

Coleta histórico de DRE via yfinance para todas as ações ativas
e atualiza os indicadores no banco de dados.

FIIs são ignorados (usam dividend_growth_yoy, já coletado).

Uso:
    python -m backend.scripts.update_income_growth
    python -m backend.scripts.update_income_growth --limit 50
    python -m backend.scripts.update_income_growth --ticker PETR4
"""

import argparse
import logging
import time
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

for lib in ["yfinance", "peewee", "urllib3"]:
    logging.getLogger(lib).setLevel(logging.WARNING)


def run(limit: int | None = None, ticker: str | None = None, delay: float = 0.5) -> None:
    """
    Atualiza crescimento de lucro e receita para todas as ações no banco.

    Args:
        limit: Limita o número de tickers processados.
        ticker: Processa apenas um ticker específico.
        delay: Delay entre requisições (segundos).
    """
    from backend.collectors.income_history import get_income_growth
    from backend.db.models import ASSET_TYPE_STOCK, Indicators, SessionLocal, Ticker
    from backend.processors.scoring import calculate_score

    db = SessionLocal()
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    try:
        # Busca ações ativas (ignora FIIs)
        query = db.query(Ticker).filter(Ticker.asset_type == ASSET_TYPE_STOCK)
        if ticker:
            query = query.filter(Ticker.symbol == ticker.upper())
        tickers = query.all()

        if limit:
            tickers = tickers[:limit]

        total = len(tickers)
        updated = 0
        skipped = 0
        no_data = 0

        logger.info("Atualizando crescimento de lucro para %d ações...", total)
        started = datetime.utcnow()

        for i, db_ticker in enumerate(tickers, 1):
            if i % 100 == 0:
                elapsed = (datetime.utcnow() - started).total_seconds()
                eta = (elapsed / i) * (total - i) if i > 1 else 0
                logger.info(
                    "Progresso: %d/%d | Atualizados: %d | Sem dados: %d | ETA: %.0fs",
                    i, total, updated, no_data, eta,
                )

            # Coleta histórico de DRE
            growth_data = get_income_growth(db_ticker.symbol)

            ni_growth = growth_data.get("net_income_growth_yoy")
            rev_growth = growth_data.get("revenue_growth_yoy")

            if ni_growth is None and rev_growth is None:
                no_data += 1
                continue

            # Busca ou cria registro de indicadores para hoje
            ind = (
                db.query(Indicators)
                .filter(
                    Indicators.ticker_id == db_ticker.id,
                    Indicators.reference_date == today,
                )
                .first()
            )

            if ind is None:
                # Busca o mais recente para não perder dados existentes
                ind = (
                    db.query(Indicators)
                    .filter(Indicators.ticker_id == db_ticker.id)
                    .order_by(Indicators.reference_date.desc())
                    .first()
                )

            if ind is None:
                skipped += 1
                continue

            # Atualiza campos de crescimento
            changed = False
            if ni_growth is not None and ind.net_income_growth_yoy != ni_growth:
                ind.net_income_growth_yoy = ni_growth
                changed = True
            if rev_growth is not None and ind.revenue_growth_yoy != rev_growth:
                ind.revenue_growth_yoy = rev_growth
                changed = True

            if changed:
                # Recalcula score com os novos dados
                indicators_dict = {
                    "pe_ratio": ind.pe_ratio,
                    "roe": ind.roe,
                    "debt_ebitda": ind.debt_ebitda,
                    "net_margin": ind.net_margin,
                    "ev_ebitda": ind.ev_ebitda,
                    "dividend_yield": ind.dividend_yield,
                    "net_income_growth_yoy": ni_growth or ind.net_income_growth_yoy,
                }
                score_result = calculate_score(indicators_dict, asset_type="stock")
                ind.score = score_result["score"]
                ind.score_label = score_result["label"]

                db.commit()
                updated += 1

            if delay > 0:
                time.sleep(delay)

    finally:
        db.close()

    duration = (datetime.utcnow() - started).total_seconds()
    logger.info(
        "Concluído em %.0fs | Atualizados: %d | Sem dados yfinance: %d | Sem registro: %d",
        duration, updated, no_data, skipped,
    )

    # Relatório rápido
    print(f"\n{'='*55}")
    print("ATUALIZAÇÃO DE CRESCIMENTO DE LUCRO (net_income_growth_yoy)")
    print(f"{'='*55}")
    print(f"Total de ações processadas : {total}")
    print(f"Atualizadas com CAGR       : {updated} ({updated/total*100:.1f}%)")
    print(f"Sem histórico yfinance     : {no_data} ({no_data/total*100:.1f}%)")
    print(f"Sem registro no banco      : {skipped}")
    print(f"{'='*55}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Atualiza crescimento de lucro via yfinance")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--ticker", type=str, default=None)
    parser.add_argument("--delay", type=float, default=0.5)
    args = parser.parse_args()

    run(limit=args.limit, ticker=args.ticker, delay=args.delay)
