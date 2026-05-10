"""
Script para tratar tickers com menos de 3 indicadores disponíveis.

Estratégia:
1. Tickers com dados no yfinance: complementa os indicadores faltantes
2. Tickers sem dados em nenhuma fonte: move para inactive_tickers

Executar após populate_all_tickers e fix_zero_indicators.
"""

import logging
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
logger = logging.getLogger(__name__)

for lib in ["yfinance", "urllib3"]:
    logging.getLogger(lib).setLevel(logging.WARNING)


def get_yfinance_indicators(symbol: str) -> dict:
    """Tenta obter indicadores via yfinance como complemento."""
    import yfinance as yf

    try:
        stock = yf.Ticker(symbol + ".SA")
        info = stock.info
        price = info.get("regularMarketPrice") or info.get("currentPrice")
        if not price:
            return {}
        return {
            "current_price": price,
            "roe": info.get("returnOnEquity"),
            "net_margin": info.get("profitMargins"),
            "pe_ratio": info.get("trailingPE") or info.get("forwardPE"),
            "pb_ratio": info.get("priceToBook"),
            "dividend_yield": info.get("dividendYield"),
        }
    except Exception:
        return {}


def count_indicators(ind) -> int:
    """Conta indicadores não nulos de um registro Indicators."""
    fields = [
        ind.roe, ind.net_margin, ind.debt_ebitda, ind.ev_ebitda,
        ind.pe_ratio, ind.pb_ratio, ind.dividend_yield,
        ind.net_income_growth_yoy, ind.revenue_growth_yoy,
    ]
    return sum(1 for f in fields if f is not None)


def run():
    from backend.db.models import (
        ASSET_TYPE_STOCK, InactiveTicker, Indicators, SessionLocal, Ticker,
    )
    from backend.processors.asset_classifier import classify_asset_type
    from backend.processors.scoring import calculate_score
    from sqlalchemy import text

    db = SessionLocal()
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    # Busca ações com menos de 3 indicadores
    rows = db.execute(text("""
        SELECT t.id, t.symbol, t.sector, t.b3_type,
               ind.id as ind_id,
               ind.roe, ind.net_margin, ind.debt_ebitda, ind.ev_ebitda,
               ind.pe_ratio, ind.pb_ratio, ind.dividend_yield,
               ind.net_income_growth_yoy, ind.revenue_growth_yoy
        FROM tickers t
        JOIN indicators ind ON ind.ticker_id = t.id
        WHERE t.asset_type = 'stock'
        AND (
            (CASE WHEN ind.roe IS NOT NULL THEN 1 ELSE 0 END +
             CASE WHEN ind.net_margin IS NOT NULL THEN 1 ELSE 0 END +
             CASE WHEN ind.pe_ratio IS NOT NULL THEN 1 ELSE 0 END +
             CASE WHEN ind.pb_ratio IS NOT NULL THEN 1 ELSE 0 END +
             CASE WHEN ind.dividend_yield IS NOT NULL THEN 1 ELSE 0 END +
             CASE WHEN ind.ev_ebitda IS NOT NULL THEN 1 ELSE 0 END) < 3
        )
    """)).fetchall()

    logger.info("Tickers com < 3 indicadores: %d", len(rows))

    complemented = 0
    moved_to_inactive = 0

    for row in rows:
        symbol = row.symbol

        # Tenta complementar via yfinance
        yf_data = get_yfinance_indicators(symbol)

        if yf_data.get("current_price"):
            # Tem dados no yfinance — complementa
            ind = db.query(Indicators).filter(Indicators.id == row.ind_id).first()
            changed = False

            for field in ["roe", "net_margin", "pe_ratio", "pb_ratio", "dividend_yield"]:
                current_val = getattr(ind, field)
                yf_val = yf_data.get(field)
                if current_val is None and yf_val is not None:
                    try:
                        yf_float = float(yf_val)
                        if yf_float != 0:
                            setattr(ind, field, yf_float)
                            changed = True
                    except (ValueError, TypeError):
                        pass

            if changed:
                # Recalcula score
                indicators_dict = {
                    "pe_ratio": ind.pe_ratio,
                    "roe": ind.roe,
                    "debt_ebitda": ind.debt_ebitda,
                    "net_margin": ind.net_margin,
                    "ev_ebitda": ind.ev_ebitda,
                    "dividend_yield": ind.dividend_yield,
                    "net_income_growth_yoy": ind.net_income_growth_yoy,
                }
                score_result = calculate_score(indicators_dict, asset_type="stock")
                ind.score = score_result["score"]
                ind.score_label = score_result["label"]
                complemented += 1
                logger.info("Complementado %s via yfinance -> score %.1f (%s)",
                            symbol, score_result["score"], score_result["label"])
        else:
            # Sem dados em nenhuma fonte — move para inactive_tickers
            existing = db.query(InactiveTicker).filter(
                InactiveTicker.symbol == symbol
            ).first()

            if not existing:
                inactive = InactiveTicker(
                    symbol=symbol,
                    name=None,
                    sector=row.sector,
                    asset_type=classify_asset_type(symbol),
                    b3_type=row.b3_type,
                    reason="sem_dados",
                    last_price=None,
                )
                db.add(inactive)

            # Remove da tabela de ativos
            ticker_obj = db.query(Ticker).filter(Ticker.id == row.id).first()
            if ticker_obj:
                db.delete(ticker_obj)  # cascade deleta indicators e financial_data

            moved_to_inactive += 1
            logger.info("Movido para inativos: %s (sem dados em fundamentus e yfinance)", symbol)

    db.commit()
    db.close()

    print(f"\n{'='*55}")
    print("RESULTADO")
    print(f"{'='*55}")
    print(f"Complementados via yfinance : {complemented}")
    print(f"Movidos para inativos       : {moved_to_inactive}")
    print(f"{'='*55}")


if __name__ == "__main__":
    run()
