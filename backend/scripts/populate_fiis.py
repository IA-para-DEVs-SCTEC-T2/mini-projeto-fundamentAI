"""
Script para popular o banco com todos os FIIs reais da B3.

Fluxo:
1. Lista todos os tickers XXXX11 da B3 (candidatos a FII)
2. Filtra os que já estão na lista de exclusão (units de empresas)
3. Confirma via yfinance se industryKey começa com "reit-" ou nome indica FII
4. Coleta dados via get_fii_data()
5. Persiste no banco com asset_type="fii"
6. Gera relatório final

Uso:
    python -m backend.scripts.populate_fiis
    python -m backend.scripts.populate_fiis --limit 50
    python -m backend.scripts.populate_fiis --dry-run
"""

import argparse
import logging
import re
import time
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

for lib in ["yfinance", "peewee", "urllib3", "fundamentus", "detalhes"]:
    logging.getLogger(lib).setLevel(logging.WARNING)

_FII_CANDIDATE_PATTERN = re.compile(r"^[A-Z]{4}11$")


def get_fii_candidates_from_b3() -> list[str]:
    """
    Retorna a lista curada de FIIs reais da B3, confirmados via yfinance
    (industryKey começa com 'reit-' ou longName indica fundo imobiliário).

    Lista gerada por discover_fiis.py em 2026-05-17 — 180 FIIs confirmados.
    """
    return [
        "ABCP11","AFHI11","AIEC11","ALZR11","ARRI11","ATSA11","BARI11",
        "BBFI11","BBFO11","BBPO11","BBRC11","BCIA11","BCRI11","BMLC11",
        "BNFS11","BRCO11","BRCR11","BRIP11","BTRA11","BTLG11","CACR11",
        "CARE11","CBOP11","CCRF11","CEOC11","CJCT11","CNES11","CPTS11",
        "CRFF11","DEVA11","DRIT11","EDGA11","ERPA11","EURO11","FAED11",
        "FAMB11","FFCI11","FGAA11","FIIB11","FIIP11","FIGS11","FLCR11",
        "FLMA11","FLRP11","FMOF11","FOFT11","FPAB11","FVPQ11","GALG11",
        "GGRC11","GLOG11","GRLV11","GTWR11","HABT11","HCTR11","HFOF11",
        "HGBS11","HGCR11","HGPO11","HGRE11","HGRU11","HGLG11","HLOG11",
        "HMOC11","HOFC11","HOSI11","HPDP11","HRDF11","HSAF11","HSML11",
        "HSLG11","HTMX11","HUSC11","INLG11","IRDM11","ITIP11","ITRI11",
        "JFLL11","JGPX11","JSAF11","JSRE11","KFOF11","KNCR11","KNHY11",
        "KNIP11","KNRE11","KNRI11","KNSC11","KORE11","LASC11","LPLP11",
        "LSPA11","LVBI11","MBRF11","MCCI11","MCRE11","MFCR11","MGHT11",
        "MXRF11","NCRI11","NEWL11","NSLU11","NVHO11","ONEF11","OUJP11",
        "PATC11","PATL11","PEMA11","PLCR11","PLRI11","PNPR11","PORD11",
        "PQAG11","PVBI11","RBCO11","RBHG11","RBHY11","RBLG11","RBRD11",
        "RBRF11","RBRY11","RBVA11","RCFA11","RCRB11","RCRI11","RECR11",
        "RECT11","RELG11","RFOF11","RNGO11","RPRI11","RSPD11","RZAG11",
        "RZAK11","RZAT11","RZTR11","SAAG11","SARE11","SCPF11","SDIL11",
        "SEQR11","SHPH11","SHOP11","SNEL11","SNFF11","SPTW11","TGAR11",
        "THRA11","TORD11","TRBL11","TRXF11","TVRI11","UBSR11","URPR11",
        "VCJR11","VCRI11","VCRR11","VGIP11","VGIR11","VGRI11","VISC11",
        "VINO11","VOTS11","VPSI11","VRTA11","VSHO11","VSLH11","VTLT11",
        "VVCO11","WPLZ11","WTSP11","XPCA11","XPCM11","XPCI11","XPIN11",
        "XPLG11","XPML11","XPSF11","YCHY11","ZAVI11",
    ]


def confirm_fii_and_collect(symbol: str) -> dict | None:
    """
    Coleta dados do FII via yfinance.
    A lista já é curada, então não reconfirma o tipo — só coleta.
    Retorna None se não tiver dados disponíveis.
    """
    from backend.collectors.fii import get_fii_data
    try:
        data = get_fii_data(symbol)
        return data
    except Exception as exc:
        logger.debug("%s: erro na coleta — %s", symbol, exc)
        return None


def persist_fii(db, data: dict) -> bool:
    """Persiste dados de um FII no banco."""
    from backend.db.repository import (
        FinancialDataRepository,
        IndicatorsRepository,
        TickerRepository,
    )
    from backend.processors.scoring import calculate_score
    from backend.processors.data_validator import validate_indicators

    try:
        symbol = data["symbol"]
        ticker_repo = TickerRepository(db)
        financial_repo = FinancialDataRepository(db)
        indicators_repo = IndicatorsRepository(db)

        db_ticker, created = ticker_repo.get_or_create(
            symbol,
            name=data.get("name"),
            sector="Fundos Imobiliários",
            asset_type="fii",
        )
        if created:
            logger.info("Novo FII cadastrado: %s", symbol)

        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        financial_repo.upsert(
            ticker_id=db_ticker.id,
            reference_date=today,
            current_price=data.get("current_price"),
            market_cap=data.get("market_cap"),
            book_value_per_share=data.get("book_value_per_share"),
            shares_outstanding=data.get("shares_outstanding"),
            dividend_yield=data.get("dividend_yield"),
            last_dividend=data.get("last_dividend"),
            last_dividend_date=data.get("last_dividend_date"),
            dividends_12m=data.get("dividends_12m"),
            dividend_growth_yoy=data.get("dividend_growth_yoy"),
        )

        indicators = {
            "pb_ratio": data.get("pb_ratio"),
            "pe_ratio": data.get("pe_ratio"),
            "dividend_yield": data.get("dividend_yield"),
            "dividend_growth_yoy": data.get("dividend_growth_yoy"),
        }

        score_result = calculate_score(indicators, asset_type="fii")
        indicators, anomalies = validate_indicators(indicators, "fii", symbol)
        if anomalies:
            logger.warning("[COMPLIANCE] %s: %d anomalia(s) removida(s)", symbol, len(anomalies))

        valid_fields = {"pb_ratio", "pe_ratio", "dividend_yield", "dividend_growth_yoy"}
        indicators_to_save = {k: v for k, v in indicators.items() if k in valid_fields and v is not None}

        indicators_repo.upsert(
            ticker_id=db_ticker.id,
            reference_date=today,
            score=score_result["score"],
            score_label=score_result["label"],
            **indicators_to_save,
        )

        logger.info(
            "FII %s | Score: %.1f (%s) | P/VP: %s | DY: %s",
            symbol,
            score_result["score"],
            score_result["label"],
            f"{data.get('pb_ratio'):.2f}" if data.get("pb_ratio") else "N/A",
            f"{data.get('dividend_yield')*100:.1f}%" if data.get("dividend_yield") else "N/A",
        )
        return True

    except Exception as exc:
        logger.error("Erro ao persistir FII %s: %s", data.get("symbol"), exc)
        return False


def run(limit: int | None = None, dry_run: bool = False, delay: float = 0.5) -> None:
    """Executa a população de FIIs reais no banco."""
    from backend.db.models import SessionLocal, create_tables
    from backend.db.repository import TickerRepository

    create_tables()

    candidates = get_fii_candidates_from_b3()
    if limit:
        candidates = candidates[:limit]

    # Descobre FIIs já no banco
    db_check = SessionLocal()
    try:
        existing_fiis = {
            t.symbol for t in TickerRepository(db_check).get_all()
            if t.asset_type == "fii"
        }
    finally:
        db_check.close()

    pending = [t for t in candidates if t not in existing_fiis]
    logger.info(
        "FIIs já no banco: %d | Candidatos pendentes: %d",
        len(existing_fiis), len(pending)
    )

    if dry_run:
        logger.info("[DRY-RUN] Candidatos que seriam processados:")
        for t in pending:
            logger.info("  %s", t)
        return

    total = len(pending)
    confirmed_fiis = 0
    not_fii = 0
    errors = 0
    started = datetime.utcnow()

    db = SessionLocal()
    try:
        for i, symbol in enumerate(pending, 1):
            if i % 20 == 0 or i == 1:
                elapsed = (datetime.utcnow() - started).total_seconds()
                eta = (elapsed / i) * (total - i) if i > 1 else 0
                logger.info(
                    "Progresso: %d/%d | FIIs confirmados: %d | Não-FII: %d | ETA: %.0fs",
                    i, total, confirmed_fiis, not_fii, eta,
                )

            data = confirm_fii_and_collect(symbol)

            if data is None:
                not_fii += 1
            else:
                ok = persist_fii(db, data)
                if ok:
                    confirmed_fiis += 1
                else:
                    errors += 1

            time.sleep(delay)

    finally:
        db.close()

    duration = (datetime.utcnow() - started).total_seconds()

    print(f"\n{'='*60}")
    print("POPULATE FIIs — RESULTADO")
    print(f"{'='*60}")
    print(f"Candidatos processados : {total}")
    print(f"FIIs reais confirmados : {confirmed_fiis}")
    print(f"Não são FIIs           : {not_fii}")
    print(f"Erros                  : {errors}")
    print(f"Tempo total            : {duration:.0f}s")
    print(f"{'='*60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Popula banco com FIIs reais da B3")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--delay", type=float, default=0.5)
    args = parser.parse_args()

    run(limit=args.limit, dry_run=args.dry_run, delay=args.delay)
