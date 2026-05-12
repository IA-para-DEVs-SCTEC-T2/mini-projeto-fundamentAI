"""
Script para corrigir indicadores com valor zero inválido no banco.

O fundamentus retorna "000" para indicadores sem dado real (P/L, P/VP, EV/EBITDA).
Esses valores foram salvos como 0.0 em vez de None.
Este script corrige os zeros e recalcula os scores afetados.
"""

from backend.db.models import SessionLocal, Indicators, Ticker
from backend.processors.scoring import calculate_score
from sqlalchemy import text

db = SessionLocal()

# Busca tickers com zeros inválidos em indicadores de valuation
rows = db.execute(text("""
    SELECT t.symbol, t.asset_type, ind.id,
           ind.pe_ratio, ind.pb_ratio, ind.ev_ebitda,
           ind.roe, ind.net_margin, ind.debt_ebitda,
           ind.dividend_yield, ind.net_income_growth_yoy
    FROM tickers t
    JOIN indicators ind ON ind.ticker_id = t.id
    WHERE (ind.pe_ratio = 0 OR ind.pb_ratio = 0 OR ind.ev_ebitda = 0)
    AND t.asset_type = 'stock'
""")).fetchall()

print(f"Tickers com zeros invalidos: {len(rows)}")

fixed = 0
for row in rows:
    ind = db.query(Indicators).filter(Indicators.id == row.id).first()
    changed = False

    if ind.pe_ratio == 0:
        ind.pe_ratio = None
        changed = True
    if ind.pb_ratio == 0:
        ind.pb_ratio = None
        changed = True
    if ind.ev_ebitda == 0:
        ind.ev_ebitda = None
        changed = True

    if changed:
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
        fixed += 1
        print(f"  {row.symbol}: score -> {score_result['score']} ({score_result['label']})")

db.commit()
db.close()
print(f"\nCorrigidos: {fixed} tickers")
