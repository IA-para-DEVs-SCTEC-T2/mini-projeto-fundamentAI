"""
Script para popular o banco com todos os tickers da B3.

Fluxo:
1. Lista todos os tickers via fundamentus.list_papel_all()
2. Classifica cada ticker como ação ou FII
3. Verifica inatividade antes de coletar dados
4. Coleta dados: ações via fundamentus, FIIs via yfinance
5. Calcula score com lógica específica por tipo de ativo
6. Persiste no banco (upsert)
7. Gera relatório de inativos e relatório de nulos

Uso:
    python -m backend.scripts.populate_all_tickers
    python -m backend.scripts.populate_all_tickers --limit 50
    python -m backend.scripts.populate_all_tickers --report-only
    python -m backend.scripts.populate_all_tickers --inactive-report
"""

import argparse
import logging
import os
import time
from datetime import datetime

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Suprime logs verbosos de bibliotecas externas
for lib in ["detalhes", "fundamentus", "logging", "yfinance", "peewee"]:
    logging.getLogger(lib).setLevel(logging.WARNING)


# ---------------------------------------------------------------------------
# Coleta de dados por tipo de ativo
# ---------------------------------------------------------------------------


def collect_stock_data(symbol: str) -> dict | None:
    """Coleta dados de uma AÇÃO via fundamentus."""
    import fundamentus  # type: ignore

    try:
        result = fundamentus.get_papel(symbol)
        if result is None or (isinstance(result, pd.DataFrame) and result.empty):
            return None

        row = result.iloc[0] if isinstance(result, pd.DataFrame) else result

        def safe(col: str, zero_is_null: bool = False) -> float | str | None:
            """
            Extrai e converte valor de uma coluna do fundamentus.

            Args:
                col: Nome da coluna.
                zero_is_null: Se True, trata 0.0 como None (para indicadores de valuation
                              onde '000' no fundamentus significa dado ausente).
            """
            try:
                val = row[col] if isinstance(row, pd.Series) else getattr(row, col, None)
                if val is None:
                    return None
                if isinstance(val, float) and pd.isna(val):
                    return None
                if isinstance(val, str):
                    val = val.strip()
                    if val in ("", "-", "N/A", "nan", "000"):
                        return None
                    has_percent = val.endswith("%")
                    val_clean = val.replace("%", "").replace(".", "").replace(",", ".").strip()
                    try:
                        num = float(val_clean)
                        if zero_is_null and num == 0.0:
                            return None
                        return num / 100 if has_percent else num
                    except ValueError:
                        return val
                if hasattr(val, "item"):
                    num = float(val.item())
                    return None if (zero_is_null and num == 0.0) else num
                num = float(val) if isinstance(val, (int, float)) else val
                if zero_is_null and isinstance(num, float) and num == 0.0:
                    return None
                return num
            except Exception:
                return None

        ev_ebitda_raw = safe("EV_EBITDA", zero_is_null=True)
        enterprise_value_raw = safe("Valor_da_firma")
        net_debt_raw = safe("Div_Liquida")

        # Deriva EBITDA e Dívida/EBITDA a partir de EV e EV/EBITDA
        # EBITDA = Valor_da_firma / EV_EBITDA
        # Dívida/EBITDA = Div_Liquida / EBITDA
        debt_ebitda_derived = None
        if (ev_ebitda_raw is not None and ev_ebitda_raw > 0
                and enterprise_value_raw is not None and enterprise_value_raw > 0
                and net_debt_raw is not None):
            ebitda_derived = enterprise_value_raw / ev_ebitda_raw
            if ebitda_derived > 0:
                debt_ebitda_derived = net_debt_raw / ebitda_derived

        return {
            "symbol": symbol,
            "asset_type": "stock",
            "name": safe("Empresa"),
            "sector": safe("Setor"),
            "segment": safe("Subsetor"),
            "b3_type": safe("Tipo"),
            "current_price": safe("Cotacao"),
            "market_cap": safe("Valor_de_mercado"),
            "enterprise_value": enterprise_value_raw,
            "shares_outstanding": safe("Nro_Acoes"),
            # Valuation — zero significa dado ausente no fundamentus
            "pe_ratio": safe("PL", zero_is_null=True),
            "pb_ratio": safe("PVP", zero_is_null=True),
            "ev_ebitda": ev_ebitda_raw,
            # Rentabilidade
            "roe": safe("ROE"),
            "roic": safe("ROIC"),
            "net_margin": safe("Marg_Liquida"),
            "ebit_margin": safe("Marg_EBIT"),
            # Endividamento
            "debt_equity": safe("Div_Liq_Patrim"),
            "debt_ebitda": debt_ebitda_derived,   # derivado de EV/EV_EBITDA
            # Dividendos
            "dividend_yield": safe("Div_Yield"),
            # Crescimento
            "revenue_growth_5y": safe("Cres_Rec_5a"),
            # Balanço
            "total_assets": safe("Ativo"),
            "cash": safe("Disponibilidades"),
            "gross_debt": safe("Div_Bruta"),
            "net_debt": net_debt_raw,
            "total_equity": safe("Patrim_Liq"),
            # DRE 12m
            "revenue": safe("Receita_Liquida_12m"),
            "ebit": safe("EBIT_12m"),
            "net_income": safe("Lucro_Liquido_12m"),
            # Por ação
            "eps": safe("LPA"),
            "book_value_per_share": safe("VPA"),
        }

    except Exception as exc:
        logger.debug("Erro ao coletar ação %s: %s", symbol, exc)
        return None


def collect_fii_data(symbol: str) -> dict | None:
    """Coleta dados de um FII via yfinance."""
    try:
        from backend.collectors.fii import get_fii_data
        data = get_fii_data(symbol)
        return data
    except (ValueError, RuntimeError) as exc:
        logger.debug("FII %s indisponível: %s", symbol, exc)
        return None
    except Exception as exc:
        logger.debug("Erro ao coletar FII %s: %s", symbol, exc)
        return None


# ---------------------------------------------------------------------------
# Persistência
# ---------------------------------------------------------------------------


def persist_ticker_data(db, data: dict) -> bool:
    """Persiste dados de um ticker (ação ou FII) no banco."""
    from datetime import datetime

    from backend.db.repository import (
        FinancialDataRepository,
        IndicatorsRepository,
        TickerRepository,
    )
    from backend.processors.scoring import calculate_score

    try:
        asset_type = data.get("asset_type", "stock")
        ticker_repo = TickerRepository(db)
        financial_repo = FinancialDataRepository(db)
        indicators_repo = IndicatorsRepository(db)

        db_ticker, _ = ticker_repo.get_or_create(
            data["symbol"],
            name=data.get("name"),
            sector=data.get("sector"),
            segment=data.get("segment"),
            asset_type=asset_type,
        )

        # Atualiza b3_type se disponível
        if data.get("b3_type") and db_ticker.b3_type != data["b3_type"]:
            db_ticker.b3_type = data.get("b3_type")
            db.commit()

        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        # Persiste dados financeiros
        financial_kwargs = {
            "current_price": data.get("current_price"),
            "market_cap": data.get("market_cap"),
        }

        if asset_type == "stock":
            financial_kwargs.update({
                "revenue": data.get("revenue"),
                "net_income": data.get("net_income"),
                "total_assets": data.get("total_assets"),
                "total_equity": data.get("total_equity"),
                "total_debt": data.get("gross_debt"),
                "net_debt": data.get("net_debt"),
                "enterprise_value": data.get("enterprise_value"),
            })
        else:  # fii
            financial_kwargs.update({
                "book_value_per_share": data.get("book_value_per_share"),
                "shares_outstanding": data.get("shares_outstanding"),
                "dividend_yield": data.get("dividend_yield"),
                "last_dividend": data.get("last_dividend"),
                "last_dividend_date": data.get("last_dividend_date"),
                "dividends_12m": data.get("dividends_12m"),
                "dividend_growth_yoy": data.get("dividend_growth_yoy"),
            })

        financial_repo.upsert(
            ticker_id=db_ticker.id,
            reference_date=today,
            **{k: v for k, v in financial_kwargs.items() if v is not None},
        )

        # Monta indicadores por tipo
        if asset_type == "stock":
            indicators = {
                "pe_ratio": data.get("pe_ratio"),
                "roe": data.get("roe"),
                "debt_ebitda": data.get("debt_ebitda"),  # derivado de Div_Liquida / (EV / EV_EBITDA)
                "net_margin": data.get("net_margin"),
                "ev_ebitda": data.get("ev_ebitda"),
                "dividend_yield": data.get("dividend_yield"),
                "net_income_growth_yoy": None,  # Requer histórico yfinance (update_income_growth)
                "pb_ratio": data.get("pb_ratio"),
                "revenue_growth_yoy": data.get("revenue_growth_5y"),
            }
        else:  # fii
            indicators = {
                "pb_ratio": data.get("pb_ratio"),
                "pe_ratio": data.get("pe_ratio"),
                "dividend_yield": data.get("dividend_yield"),
                "dividend_growth_yoy": data.get("dividend_growth_yoy"),
            }

        score_result = calculate_score(indicators, asset_type=asset_type)

        # Valida ranges antes de persistir (compliance)
        from backend.processors.data_validator import validate_indicators
        indicators, anomalies = validate_indicators(indicators, asset_type, data["symbol"])
        if anomalies:
            logger.warning("[COMPLIANCE] %s: %d indicador(es) fora do range removido(s)",
                           data["symbol"], len(anomalies))

        valid_fields = {
            "roe", "roic", "net_margin", "debt_ebitda", "ev_ebitda",
            "pe_ratio", "pb_ratio", "dividend_yield", "dividend_growth_yoy",
            "revenue_growth_yoy", "net_income_growth_yoy",
        }
        indicators_to_save = {
            k: v for k, v in indicators.items()
            if k in valid_fields and v is not None
        }

        indicators_repo.upsert(
            ticker_id=db_ticker.id,
            reference_date=today,
            score=score_result["score"],
            score_label=score_result["label"],
            **indicators_to_save,
        )

        return True

    except Exception as exc:
        logger.debug("Erro ao persistir %s: %s", data.get("symbol"), exc)
        return False


# ---------------------------------------------------------------------------
# Relatórios
# ---------------------------------------------------------------------------


def generate_null_report(output_path: str = None) -> pd.DataFrame:
    """Gera relatório de campos nulos por ticker no banco."""
    from backend.scripts._report_utils import report_path
    if output_path is None:
        output_path = report_path("banco_analise_nulos.csv")
    from backend.db.models import FinancialData, Indicators, SessionLocal, Ticker

    db = SessionLocal()
    try:
        tickers = db.query(Ticker).all()
        rows = []

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

            row = {
                "ticker": t.symbol,
                "name": t.name,
                "sector": t.sector,
                "asset_type": t.asset_type,
                "current_price": fin.current_price if fin else None,
                "market_cap": fin.market_cap if fin else None,
                # Ações
                "revenue": fin.revenue if fin else None,
                "net_income": fin.net_income if fin else None,
                "total_equity": fin.total_equity if fin else None,
                "net_debt": fin.net_debt if fin else None,
                "roe": ind.roe if ind else None,
                "net_margin": ind.net_margin if ind else None,
                "debt_ebitda": ind.debt_ebitda if ind else None,
                "ev_ebitda": ind.ev_ebitda if ind else None,
                "net_income_growth_yoy": ind.net_income_growth_yoy if ind else None,
                # Comuns
                "pe_ratio": ind.pe_ratio if ind else None,
                "pb_ratio": ind.pb_ratio if ind else None,
                "dividend_yield": ind.dividend_yield if ind else None,
                # FIIs
                "dividend_growth_yoy": ind.dividend_growth_yoy if ind else None,
                # Score
                "score": ind.score if ind else None,
                "score_label": ind.score_label if ind else None,
            }
            rows.append(row)

        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        logger.info("CSV exportado: %s (%d tickers)", output_path, len(df))

        # Resumo
        print("\n" + "=" * 65)
        print("RELATÓRIO DE CAMPOS NULOS")
        print("=" * 65)
        print(f"Total de tickers ativos no banco: {len(df)}")

        stocks = df[df["asset_type"] == "stock"]
        fiis = df[df["asset_type"] == "fii"]
        print(f"  Ações: {len(stocks)} | FIIs: {len(fiis)}")
        print()

        print(f"{'Campo':<28} {'Preench.':>10} {'Nulos':>8} {'% Nulo':>8}")
        print("-" * 65)

        cols_stocks = ["current_price", "revenue", "net_income", "total_equity",
                       "roe", "net_margin", "ev_ebitda", "pe_ratio", "pb_ratio",
                       "dividend_yield", "net_income_growth_yoy", "score"]
        cols_fiis = ["current_price", "pb_ratio", "pe_ratio",
                     "dividend_yield", "dividend_growth_yoy", "score"]

        print("  --- AÇÕES ---")
        for col in cols_stocks:
            if col in stocks.columns:
                nulos = stocks[col].isna().sum()
                preen = len(stocks) - nulos
                pct = nulos / len(stocks) * 100 if len(stocks) > 0 else 0
                print(f"  {col:<26} {preen:>10} {nulos:>8} {pct:>7.1f}%")

        print("\n  --- FIIs ---")
        for col in cols_fiis:
            if col in fiis.columns:
                nulos = fiis[col].isna().sum()
                preen = len(fiis) - nulos
                pct = nulos / len(fiis) * 100 if len(fiis) > 0 else 0
                print(f"  {col:<26} {preen:>10} {nulos:>8} {pct:>7.1f}%")

        print("\n  --- DISTRIBUIÇÃO DE SCORES ---")
        for label, count in df["score_label"].value_counts(dropna=False).items():
            pct = count / len(df) * 100
            print(f"  {str(label):<15}: {count:>4} ({pct:.1f}%)")

        print("=" * 65)
        return df

    finally:
        db.close()


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------


def run(
    limit: int | None = None,
    report_only: bool = False,
    inactive_report: bool = False,
    delay: float = 0.2,
) -> None:
    """Executa a população completa do banco."""
    import fundamentus  # type: ignore

    from backend.db.models import SessionLocal, create_tables
    from backend.db.repository import TickerRepository
    from backend.processors.asset_classifier import (
        classify_asset_type,
        generate_inactive_report,
        is_inactive,
        persist_inactive_tickers,
    )

    create_tables()

    if report_only:
        generate_null_report()
        return

    # Lista todos os tickers da B3
    all_tickers = fundamentus.list_papel_all()
    logger.info("Total de tickers na B3: %d", len(all_tickers))

    if limit:
        all_tickers = all_tickers[:limit]

    # Descobre tickers já no banco para retomar
    db_check = SessionLocal()
    try:
        existing = {t.symbol for t in TickerRepository(db_check).get_all()}
    finally:
        db_check.close()

    pending = [t for t in all_tickers if t not in existing]
    logger.info("Já no banco: %d | Pendentes: %d", len(existing), len(pending))

    total = len(pending)
    success = 0
    failed = 0
    skipped = 0
    inactive_list = []

    db = SessionLocal()
    started = datetime.utcnow()

    try:
        for i, symbol in enumerate(pending, 1):
            if i % 50 == 0 or i == 1:
                elapsed = (datetime.utcnow() - started).total_seconds()
                eta = (elapsed / i) * (total - i) if i > 1 else 0
                logger.info(
                    "Progresso: %d/%d (%.1f%%) | OK: %d | Inativo: %d | Falha: %d | ETA: %.0fs",
                    i, total, i / total * 100, success, skipped, failed, eta,
                )

            asset_type = classify_asset_type(symbol)

            # Coleta dados
            if asset_type == "fii":
                data = collect_fii_data(symbol)
            else:
                data = collect_stock_data(symbol)

            if data is None:
                # Sem dados = inativo
                inactive_list.append({
                    "symbol": symbol,
                    "name": None,
                    "sector": None,
                    "b3_type": None,
                    "reason": "sem_dados",
                    "last_price": None,
                })
                skipped += 1
                continue

            # Verifica inatividade
            inactive, reason = is_inactive(
                symbol=symbol,
                current_price=data.get("current_price"),
                net_income=data.get("net_income"),
                total_equity=data.get("total_equity"),
                roe=data.get("roe"),
                pe_ratio=data.get("pe_ratio"),
                pb_ratio=data.get("pb_ratio"),
            )

            if inactive:
                inactive_list.append({
                    "symbol": symbol,
                    "name": data.get("name"),
                    "sector": data.get("sector"),
                    "b3_type": data.get("b3_type"),
                    "reason": reason,
                    "last_price": data.get("current_price"),
                })
                skipped += 1
                logger.debug("Inativo: %s (%s)", symbol, reason)
                continue

            # Persiste
            ok = persist_ticker_data(db, data)
            if ok:
                success += 1
            else:
                failed += 1

            if delay > 0:
                time.sleep(delay)

    finally:
        # Persiste inativos no banco
        if inactive_list:
            persist_inactive_tickers(db, inactive_list)
        db.close()

    duration = (datetime.utcnow() - started).total_seconds()
    logger.info(
        "Concluído em %.0fs | Sucesso: %d | Inativos: %d | Falha: %d",
        duration, success, skipped, failed,
    )

    # Relatório de inativos
    if inactive_list:
        from backend.scripts._report_utils import report_path
        generate_inactive_report(inactive_list, report_path("relatorio_inativos.csv"))

    # Relatório de nulos
    generate_null_report()
    generate_null_report()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Popula banco com todos os tickers da B3")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--report-only", action="store_true")
    parser.add_argument("--inactive-report", action="store_true")
    parser.add_argument("--delay", type=float, default=0.2)
    args = parser.parse_args()

    run(
        limit=args.limit,
        report_only=args.report_only,
        inactive_report=args.inactive_report,
        delay=args.delay,
    )
