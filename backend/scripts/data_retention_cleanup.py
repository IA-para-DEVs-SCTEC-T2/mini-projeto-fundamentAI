"""
Script de limpeza de dados conforme política de retenção.

Política definida em docs/compliance.md:
- financial_data: 2 anos
- indicators:     2 anos
- analyses:       1 ano
- inactive_tickers: 1 ano após last_checked_at

Executar trimestralmente.

Uso:
    python -m backend.scripts.data_retention_cleanup
    python -m backend.scripts.data_retention_cleanup --dry-run
"""

import argparse
import logging
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Política de retenção (em dias)
RETENTION_POLICY = {
    "financial_data":   365 * 2,   # 2 anos
    "indicators":       365 * 2,   # 2 anos
    "analyses":         365 * 1,   # 1 ano
    "inactive_tickers": 365 * 1,   # 1 ano após last_checked_at
}


def run(dry_run: bool = False) -> dict:
    """
    Executa a limpeza de dados conforme a política de retenção.

    Args:
        dry_run: Se True, apenas reporta sem deletar.

    Returns:
        Dicionário com contagem de registros removidos por tabela.
    """
    from backend.db.models import (
        Analysis, FinancialData, InactiveTicker, Indicators, SessionLocal,
    )

    db = SessionLocal()
    report = {}
    now = datetime.utcnow()

    try:
        # --- financial_data ---
        cutoff_fin = now - timedelta(days=RETENTION_POLICY["financial_data"])
        query_fin = db.query(FinancialData).filter(FinancialData.reference_date < cutoff_fin)
        count_fin = query_fin.count()
        if not dry_run and count_fin > 0:
            query_fin.delete(synchronize_session=False)
        report["financial_data"] = count_fin
        logger.info("financial_data: %d registros anteriores a %s %s",
                    count_fin, cutoff_fin.date(), "(simulado)" if dry_run else "removidos")

        # --- indicators ---
        cutoff_ind = now - timedelta(days=RETENTION_POLICY["indicators"])
        query_ind = db.query(Indicators).filter(Indicators.reference_date < cutoff_ind)
        count_ind = query_ind.count()
        if not dry_run and count_ind > 0:
            query_ind.delete(synchronize_session=False)
        report["indicators"] = count_ind
        logger.info("indicators: %d registros anteriores a %s %s",
                    count_ind, cutoff_ind.date(), "(simulado)" if dry_run else "removidos")

        # --- analyses ---
        cutoff_ana = now - timedelta(days=RETENTION_POLICY["analyses"])
        query_ana = db.query(Analysis).filter(Analysis.generated_at < cutoff_ana)
        count_ana = query_ana.count()
        if not dry_run and count_ana > 0:
            query_ana.delete(synchronize_session=False)
        report["analyses"] = count_ana
        logger.info("analyses: %d registros anteriores a %s %s",
                    count_ana, cutoff_ana.date(), "(simulado)" if dry_run else "removidos")

        # --- inactive_tickers ---
        cutoff_ina = now - timedelta(days=RETENTION_POLICY["inactive_tickers"])
        query_ina = db.query(InactiveTicker).filter(
            InactiveTicker.last_checked_at < cutoff_ina
        )
        count_ina = query_ina.count()
        if not dry_run and count_ina > 0:
            query_ina.delete(synchronize_session=False)
        report["inactive_tickers"] = count_ina
        logger.info("inactive_tickers: %d registros anteriores a %s %s",
                    count_ina, cutoff_ina.date(), "(simulado)" if dry_run else "removidos")

        if not dry_run:
            db.commit()

    except Exception as exc:
        db.rollback()
        logger.error("Erro durante limpeza: %s", exc)
        raise
    finally:
        db.close()

    prefix = "[DRY RUN] " if dry_run else ""
    total = sum(report.values())
    print(f"\n{'='*55}")
    print(f"{prefix}LIMPEZA DE RETENÇÃO DE DADOS")
    print(f"{'='*55}")
    for table, count in report.items():
        print(f"  {table:<25}: {count} registros")
    print(f"  {'TOTAL':<25}: {total} registros")
    print(f"{'='*55}")

    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Limpeza de dados conforme política de retenção")
    parser.add_argument("--dry-run", action="store_true", help="Apenas reporta sem deletar")
    args = parser.parse_args()
    run(dry_run=args.dry_run)
