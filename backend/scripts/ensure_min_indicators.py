"""
Verificação e enriquecimento de indicadores — mínimo de 3 por ticker.

Este script faz parte do ciclo de atualização de dados e deve ser executado
após cada rodada do ETL ou populate_all_tickers.

Fluxo por ticker com < 3 indicadores:
1. Tenta complementar via fonte alternativa (yfinance para ações, cálculo para FIIs)
2. Tenta calcular indicadores derivados a partir dos dados já disponíveis no banco
3. Se ainda < 3 após todas as tentativas → move para inactive_tickers

Indicadores alvo por tipo de ativo:
  Ações:  pe_ratio, roe, debt_ebitda, net_margin, ev_ebitda, dividend_yield,
          net_income_growth_yoy, revenue_growth_yoy  (mínimo 3 de 8)
  FIIs:   pb_ratio, pe_ratio, dividend_yield, dividend_growth_yoy  (mínimo 3 de 4)

Uso:
    python -m backend.scripts.ensure_min_indicators
    python -m backend.scripts.ensure_min_indicators --dry-run   # apenas relatorio
    python -m backend.scripts.ensure_min_indicators --ticker PETR4
"""

import argparse
import logging
import warnings
from datetime import datetime, timedelta
from typing import Optional

warnings.filterwarnings("ignore")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

for lib in ["yfinance", "urllib3", "peewee", "detalhes", "fundamentus"]:
    logging.getLogger(lib).setLevel(logging.WARNING)

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

MIN_INDICATORS = 3

# Indicadores alvo por tipo de ativo
STOCK_INDICATORS = [
    "pe_ratio", "roe", "debt_ebitda", "net_margin",
    "ev_ebitda", "dividend_yield", "net_income_growth_yoy", "revenue_growth_yoy",
]
FII_INDICATORS = [
    "pb_ratio", "pe_ratio", "dividend_yield", "dividend_growth_yoy",
]


# ---------------------------------------------------------------------------
# Contagem de indicadores
# ---------------------------------------------------------------------------


def count_available(ind, asset_type: str) -> int:
    """Conta indicadores não nulos para um registro Indicators."""
    fields = STOCK_INDICATORS if asset_type == "stock" else FII_INDICATORS
    return sum(1 for f in fields if getattr(ind, f, None) is not None)


def get_missing(ind, asset_type: str) -> list[str]:
    """Retorna lista de indicadores ausentes."""
    fields = STOCK_INDICATORS if asset_type == "stock" else FII_INDICATORS
    return [f for f in fields if getattr(ind, f, None) is None]


# ---------------------------------------------------------------------------
# Estratégia 1: Complementar via yfinance
# ---------------------------------------------------------------------------


def enrich_from_yfinance(symbol: str, asset_type: str) -> dict:
    """
    Tenta obter indicadores faltantes via yfinance.

    Para ações: ROE, Margem, P/L, P/VP, DY via info
    Para FIIs: P/VP, P/L, DY via info + histórico de dividendos

    Returns:
        Dicionário com indicadores encontrados (apenas os não nulos).
    """
    import yfinance as yf
    import pandas as pd

    result = {}
    try:
        stock = yf.Ticker(symbol + ".SA")
        info = stock.info
        price = info.get("regularMarketPrice") or info.get("currentPrice")

        if not price:
            return result

        # Campos comuns
        _safe_set(result, "pe_ratio", info.get("trailingPE") or info.get("forwardPE"))
        _safe_set(result, "pb_ratio", info.get("priceToBook"))
        _safe_set(result, "dividend_yield", info.get("dividendYield"))

        if asset_type == "stock":
            _safe_set(result, "roe", info.get("returnOnEquity"))
            _safe_set(result, "net_margin", info.get("profitMargins"))

        elif asset_type == "fii":
            # DY calculado a partir do histórico de dividendos (últimos 12m)
            if "dividend_yield" not in result:
                dy_calc = _calculate_dy_from_history(stock, price)
                if dy_calc:
                    result["dividend_yield"] = dy_calc

            # Crescimento de dividendos via histórico
            if "dividend_growth_yoy" not in result:
                dg = _calculate_dividend_growth_from_history(stock)
                if dg is not None:
                    result["dividend_growth_yoy"] = dg

    except Exception as exc:
        logger.debug("yfinance indisponível para %s: %s", symbol, exc)

    return result


def _safe_set(d: dict, key: str, value) -> None:
    """Adiciona ao dicionário apenas se o valor for válido (não None, não zero)."""
    if value is None:
        return
    try:
        v = float(value)
        if v != 0.0:
            d[key] = v
    except (ValueError, TypeError):
        pass


def _calculate_dy_from_history(stock, price: float) -> Optional[float]:
    """Calcula DY dos últimos 12 meses a partir do histórico de dividendos."""
    import pandas as pd

    try:
        divs = stock.dividends
        if divs is None or divs.empty:
            return None
        divs.index = pd.to_datetime(divs.index, utc=True)
        cutoff = pd.Timestamp(datetime.utcnow() - timedelta(days=365), tz="UTC")
        divs_12m = divs[divs.index >= cutoff]
        total = float(divs_12m.sum())
        if total > 0 and price > 0:
            return total / price
    except Exception:
        pass
    return None


def _calculate_dividend_growth_from_history(stock) -> Optional[float]:
    """Calcula CAGR de dividendos anuais a partir do histórico."""
    import pandas as pd

    try:
        divs = stock.dividends
        if divs is None or divs.empty or len(divs) < 2:
            return None
        divs.index = pd.to_datetime(divs.index, utc=True)
        annual = divs.groupby(divs.index.year).sum()
        annual = annual[annual > 0]
        if len(annual) < 2:
            return None
        initial = float(annual.iloc[-1])
        final = float(annual.iloc[0])
        n = len(annual) - 1
        if initial <= 0 or final <= 0:
            return None
        return round((final / initial) ** (1 / n) - 1, 6)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Estratégia 2: Calcular indicadores derivados a partir do banco
# ---------------------------------------------------------------------------


def derive_indicators(ind, fin, asset_type: str) -> dict:
    """
    Calcula indicadores derivados a partir dos dados financeiros já no banco.

    Ações:
    - ROE = net_income / total_equity
    - net_margin = net_income / revenue
    - debt_ebitda = net_debt / ebitda (se disponível)
    - pe_ratio = current_price / (net_income / shares) — se tivermos shares

    FIIs:
    - dividend_yield = dividends_12m / current_price
    - pb_ratio = current_price / book_value_per_share

    Args:
        ind: Registro Indicators do banco.
        fin: Registro FinancialData mais recente do banco.
        asset_type: "stock" ou "fii".

    Returns:
        Dicionário com indicadores calculados (apenas os não nulos).
    """
    result = {}

    if fin is None:
        return result

    if asset_type == "stock":
        price = fin.current_price
        net_income = fin.net_income
        revenue = fin.revenue
        total_equity = fin.total_equity
        net_debt = fin.net_debt
        ebitda = fin.ebitda

        # ROE = Lucro / Patrimônio
        if ind.roe is None and net_income and total_equity and total_equity != 0:
            result["roe"] = net_income / total_equity

        # Margem Líquida = Lucro / Receita
        if ind.net_margin is None and net_income and revenue and revenue != 0:
            result["net_margin"] = net_income / revenue

        # Dívida/EBITDA
        if ind.debt_ebitda is None and net_debt is not None and ebitda and ebitda > 0:
            result["debt_ebitda"] = net_debt / ebitda

    elif asset_type == "fii":
        price = fin.current_price
        bvps = fin.book_value_per_share
        divs_12m = fin.dividends_12m

        # P/VP = Preço / VPA
        if ind.pb_ratio is None and price and bvps and bvps > 0:
            result["pb_ratio"] = price / bvps

        # DY = Dividendos 12m / Preço
        if ind.dividend_yield is None and divs_12m and price and price > 0:
            result["dividend_yield"] = divs_12m / price

    return result


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------


def run(
    dry_run: bool = False,
    ticker_filter: Optional[str] = None,
    move_to_inactive: bool = True,
) -> dict:
    """
    Verifica e enriquece indicadores para todos os tickers com < 3 disponíveis.

    Args:
        dry_run: Se True, apenas reporta sem alterar o banco.
        ticker_filter: Processa apenas um ticker específico.
        move_to_inactive: Se True, move para inativos os que não atingirem o mínimo.

    Returns:
        Relatório com contagens de cada ação tomada.
    """
    from backend.db.models import (
        ASSET_TYPE_FII, ASSET_TYPE_STOCK,
        FinancialData, InactiveTicker, Indicators, SessionLocal, Ticker,
    )
    from backend.processors.asset_classifier import classify_asset_type
    from backend.processors.scoring import calculate_score

    db = SessionLocal()
    report = {
        "checked": 0,
        "already_ok": 0,
        "enriched_yfinance": 0,
        "enriched_derived": 0,
        "still_below_min": 0,
        "moved_to_inactive": 0,
        "details": [],
    }

    try:
        query = db.query(Ticker)
        if ticker_filter:
            query = query.filter(Ticker.symbol == ticker_filter.upper())
        tickers = query.all()

        logger.info("Verificando %d tickers (mínimo %d indicadores)...", len(tickers), MIN_INDICATORS)

        for t in tickers:
            ind = (
                db.query(Indicators)
                .filter(Indicators.ticker_id == t.id)
                .order_by(Indicators.reference_date.desc())
                .first()
            )
            fin = (
                db.query(FinancialData)
                .filter(FinancialData.ticker_id == t.id)
                .order_by(FinancialData.reference_date.desc())
                .first()
            )

            if ind is None:
                continue

            report["checked"] += 1
            n_before = count_available(ind, t.asset_type)

            if n_before >= MIN_INDICATORS:
                report["already_ok"] += 1
                continue

            missing = get_missing(ind, t.asset_type)
            logger.info(
                "%s (%s): %d/%d indicadores | Faltando: %s",
                t.symbol, t.asset_type, n_before,
                len(STOCK_INDICATORS if t.asset_type == "stock" else FII_INDICATORS),
                missing,
            )

            enriched_any = False

            # --- Estratégia 1: yfinance ---
            yf_data = enrich_from_yfinance(t.symbol, t.asset_type)
            if yf_data:
                for field, value in yf_data.items():
                    if getattr(ind, field, None) is None and field in missing:
                        if not dry_run:
                            setattr(ind, field, value)
                        enriched_any = True
                        logger.info("  [yfinance] %s.%s = %s", t.symbol, field, value)

            # --- Estratégia 2: cálculo derivado ---
            derived = derive_indicators(ind, fin, t.asset_type)
            if derived:
                for field, value in derived.items():
                    if getattr(ind, field, None) is None and field in missing:
                        if not dry_run:
                            setattr(ind, field, value)
                        enriched_any = True
                        logger.info("  [derivado] %s.%s = %s", t.symbol, field, value)

            # Recalcula score se houve enriquecimento
            if enriched_any and not dry_run:
                indicators_dict = {
                    f: getattr(ind, f, None)
                    for f in (STOCK_INDICATORS if t.asset_type == "stock" else FII_INDICATORS)
                }
                score_result = calculate_score(indicators_dict, asset_type=t.asset_type)
                ind.score = score_result["score"]
                ind.score_label = score_result["label"]
                db.flush()

            n_after = count_available(ind, t.asset_type) if not dry_run else (
                n_before + len(yf_data) + len(derived)
            )

            if enriched_any:
                if n_before < MIN_INDICATORS and n_after >= MIN_INDICATORS:
                    report["enriched_yfinance"] += 1 if yf_data else 0
                    report["enriched_derived"] += 1 if derived else 0
                    logger.info(
                        "  OK: %s enriquecido %d -> %d indicadores",
                        t.symbol, n_before, n_after,
                    )
                else:
                    report["enriched_yfinance"] += 1 if yf_data else 0
                    report["enriched_derived"] += 1 if derived else 0

            if n_after < MIN_INDICATORS:
                report["still_below_min"] += 1
                report["details"].append({
                    "symbol": t.symbol,
                    "asset_type": t.asset_type,
                    "n_before": n_before,
                    "n_after": n_after,
                    "missing": missing,
                })

                if move_to_inactive and not dry_run:
                    # Move para inactive_tickers
                    existing = db.query(InactiveTicker).filter(
                        InactiveTicker.symbol == t.symbol
                    ).first()
                    if not existing:
                        db.add(InactiveTicker(
                            symbol=t.symbol,
                            name=t.name,
                            sector=t.sector,
                            asset_type=t.asset_type,
                            b3_type=t.b3_type,
                            reason="sem_dados",
                            last_price=fin.current_price if fin else None,
                        ))
                    db.delete(t)  # cascade deleta indicators e financial_data
                    report["moved_to_inactive"] += 1
                    logger.warning(
                        "  INATIVO: %s movido (apenas %d indicadores disponíveis)",
                        t.symbol, n_after,
                    )

        if not dry_run:
            db.commit()

    finally:
        db.close()

    # Imprime relatório
    _print_report(report, dry_run)
    return report


def _print_report(report: dict, dry_run: bool) -> None:
    prefix = "[DRY RUN] " if dry_run else ""
    print(f"\n{'='*60}")
    print(f"{prefix}RELATÓRIO — VERIFICAÇÃO DE INDICADORES MÍNIMOS")
    print(f"{'='*60}")
    print(f"Tickers verificados       : {report['checked']}")
    print(f"Já com 3+ indicadores     : {report['already_ok']}")
    print(f"Enriquecidos via yfinance : {report['enriched_yfinance']}")
    print(f"Enriquecidos via cálculo  : {report['enriched_derived']}")
    print(f"Ainda abaixo do mínimo    : {report['still_below_min']}")
    print(f"Movidos para inativos     : {report['moved_to_inactive']}")

    if report["details"]:
        print(f"\nTickers que não atingiram o mínimo:")
        for d in report["details"]:
            print(f"  {d['symbol']:<8} ({d['asset_type']}) | {d['n_before']} -> {d['n_after']} ind | faltando: {d['missing']}")
    print(f"{'='*60}")


# ---------------------------------------------------------------------------
# Integração com o ETL
# ---------------------------------------------------------------------------


def run_after_etl(db_session=None) -> dict:
    """
    Versão para ser chamada diretamente pelo pipeline ETL após cada atualização.

    Não move para inativos automaticamente — apenas enriquece.
    Tickers que persistirem com < 3 são logados para revisão manual.

    Args:
        db_session: Sessão do banco (opcional — cria uma nova se não fornecida).

    Returns:
        Relatório de enriquecimento.
    """
    logger.info("[ETL] Iniciando verificação de indicadores mínimos...")
    report = run(dry_run=False, move_to_inactive=False)
    logger.info(
        "[ETL] Verificação concluída | Enriquecidos: %d | Abaixo do mínimo: %d",
        report["enriched_yfinance"] + report["enriched_derived"],
        report["still_below_min"],
    )
    return report


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Verifica e enriquece indicadores — mínimo 3 por ticker"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Apenas reporta sem alterar o banco",
    )
    parser.add_argument(
        "--ticker",
        type=str,
        default=None,
        help="Processa apenas um ticker específico",
    )
    parser.add_argument(
        "--no-move-inactive",
        action="store_true",
        help="Não move para inativos os que ficarem abaixo do mínimo",
    )
    args = parser.parse_args()

    run(
        dry_run=args.dry_run,
        ticker_filter=args.ticker,
        move_to_inactive=not args.no_move_inactive,
    )
