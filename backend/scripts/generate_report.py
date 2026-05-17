"""
Gera relatório de qualidade do banco de dados em Markdown.

Cobre:
- Visão geral do banco
- Distribuição de scores (geral, ações, FIIs)
- Cobertura de indicadores por tipo de ativo
- Top 20 ações e FIIs por score
- Tickers inativos
- Pontos de atenção

Uso:
    python -m backend.scripts.generate_report
    python -m backend.scripts.generate_report --output relatorio_banco.md
"""

import argparse
import sqlite3
from datetime import datetime
from pathlib import Path


def get_db_path() -> str:
    """Localiza o banco de dados."""
    candidates = [
        Path("fundamentai.db"),
        Path("backend/fundamentai.db"),
        Path("../fundamentai.db"),
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    raise FileNotFoundError("Banco fundamentai.db não encontrado.")


def pct_bar(value: float, width: int = 20) -> str:
    """Gera uma barra de progresso em texto."""
    filled = round(value / 100 * width)
    return "█" * filled + "░" * (width - filled)


def generate_report(output_path: str = None) -> str:
    """Gera o relatório completo em Markdown e retorna o conteúdo."""

    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = []

    def h(text, level=2):
        lines.append(f"\n{'#' * level} {text}\n")

    def row(*cols, widths=None):
        if widths:
            parts = [str(c).ljust(w) for c, w in zip(cols, widths)]
        else:
            parts = [str(c) for c in cols]
        lines.append("| " + " | ".join(parts) + " |")

    def divider(widths):
        lines.append("|" + "|".join("-" * (w + 2) for w in widths) + "|")

    # ── CABEÇALHO ─────────────────────────────────────────────────────────
    lines.append(f"# Relatório do Banco de Dados — FundamentAI")
    lines.append(f"\n> Gerado em: **{now}**\n")
    lines.append("---")

    # ── VISÃO GERAL ────────────────────────────────────────────────────────
    h("1. Visão Geral")

    cur.execute("SELECT COUNT(*) FROM tickers")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM inactive_tickers")
    inativos = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM indicators WHERE score IS NOT NULL")
    com_score = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM analyses")
    analises = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tickers WHERE asset_type='stock'")
    n_stocks = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tickers WHERE asset_type='fii'")
    n_fiis = cur.fetchone()[0]

    lines.append("| Métrica | Valor |")
    lines.append("|---|---|")
    lines.append(f"| Tickers ativos | **{total}** |")
    lines.append(f"| — Ações | {n_stocks} |")
    lines.append(f"| — FIIs | {n_fiis} |")
    lines.append(f"| Tickers inativos | {inativos} |")
    lines.append(f"| Com score calculado | {com_score} / {total} |")
    lines.append(f"| Análises LLM geradas | {analises} |")

    # ── DISTRIBUIÇÃO DE SCORES ─────────────────────────────────────────────
    h("2. Distribuição de Scores")

    h("2.1 Geral", level=3)
    cur.execute("""
        SELECT score_label, COUNT(*) as n,
               ROUND(AVG(score),1) as media,
               ROUND(MIN(score),1) as minimo,
               ROUND(MAX(score),1) as maximo
        FROM indicators WHERE score IS NOT NULL
        GROUP BY score_label ORDER BY media DESC
    """)
    rows_data = cur.fetchall()

    lines.append("| Label | Qtd | % | Barra | Média | Mín | Máx |")
    lines.append("|---|---:|---:|---|---:|---:|---:|")
    for r in rows_data:
        pct = r['n'] / com_score * 100
        bar = pct_bar(pct, 15)
        lines.append(f"| **{r['score_label']}** | {r['n']} | {pct:.1f}% | `{bar}` | {r['media']} | {r['minimo']} | {r['maximo']} |")

    h("2.2 Ações vs FIIs", level=3)
    for at in ('stock', 'fii'):
        label = "Ações" if at == "stock" else "FIIs"
        cur.execute("SELECT COUNT(*) FROM tickers WHERE asset_type=?", (at,))
        n = cur.fetchone()[0]
        cur.execute("""
            SELECT i.score_label, COUNT(*) as qtd,
                   ROUND(AVG(i.score),1) as media,
                   ROUND(MIN(i.score),1) as minimo,
                   ROUND(MAX(i.score),1) as maximo
            FROM indicators i JOIN tickers t ON i.ticker_id=t.id
            WHERE i.score IS NOT NULL AND t.asset_type=?
            GROUP BY i.score_label ORDER BY media DESC
        """, (at,))
        rows_at = cur.fetchall()
        lines.append(f"\n**{label}** ({n} tickers)\n")
        lines.append("| Label | Qtd | % | Média | Mín | Máx |")
        lines.append("|---|---:|---:|---:|---:|---:|")
        for r in rows_at:
            pct = r['qtd'] / n * 100
            lines.append(f"| {r['score_label']} | {r['qtd']} | {pct:.1f}% | {r['media']} | {r['minimo']} | {r['maximo']} |")

    # ── COBERTURA DE INDICADORES — AÇÕES ──────────────────────────────────
    h("3. Cobertura de Indicadores — Ações")

    lines.append(f"> Base: **{n_stocks} ações** ativas no banco\n")
    lines.append("> Indicadores ausentes recebem **score neutro (50)** no cálculo.\n")

    campos_stock = [
        ("roe",                   "ROE",                    "Retorno sobre Patrimônio",    "Peso 20% no score"),
        ("net_margin",            "Margem Líquida",         "Lucro / Receita",             "Peso 15% no score"),
        ("pe_ratio",              "P/L",                    "Preço / Lucro",               "Peso 15% no score"),
        ("pb_ratio",              "P/VP",                   "Preço / Valor Patrimonial",   "Calculado via fundamentus"),
        ("ev_ebitda",             "EV/EBITDA",              "Valor Empresa / EBITDA",      "Peso 10% no score"),
        ("debt_ebitda",           "Dívida/EBITDA",          "Dívida Líquida / EBITDA",     "Peso 15% no score — derivado de EV/EV_EBITDA"),
        ("dividend_yield",        "Dividend Yield",         "Dividendos / Preço",          "Peso 10% no score"),
        ("net_income_growth_yoy", "CAGR Lucro",             "Crescimento anual do lucro",  "Peso 15% — via yfinance (~44.7% cobertura esperada)"),
        ("revenue_growth_yoy",    "Crescimento Receita 5a", "CAGR receita 5 anos",         "Via fundamentus"),
    ]

    lines.append("| Indicador | Preenchidos | Nulos | Cobertura | Barra | Observação |")
    lines.append("|---|---:|---:|---:|---|---|")
    for col, label, _, obs in campos_stock:
        cur.execute(f"""
            SELECT COUNT(*) FROM indicators i
            JOIN tickers t ON i.ticker_id=t.id
            WHERE t.asset_type='stock' AND i.{col} IS NOT NULL
        """)
        p = cur.fetchone()[0]
        nulos = n_stocks - p
        pct = p / n_stocks * 100
        bar = pct_bar(pct, 15)
        status = "✅" if pct >= 80 else ("⚠️" if pct >= 40 else "❌")
        lines.append(f"| **{label}** | {p} | {nulos} | {pct:.1f}% | `{bar}` {status} | {obs} |")

    # ── COBERTURA DE INDICADORES — FIIs ───────────────────────────────────
    h("4. Cobertura de Indicadores — FIIs")

    lines.append(f"> Base: **{n_fiis} FIIs** ativos no banco\n")
    lines.append("> Fonte exclusiva: **yfinance** (fundamentus não suporta FIIs).\n")

    campos_fii = [
        ("pb_ratio",           "P/VP",             "Preço / Valor Patrimonial por Cota", "Peso 30% no score — yfinance retorna `priceToBook`"),
        ("pe_ratio",           "P/L",              "Preço / Lucro",                      "Peso 15% no score — via `trailingPE`"),
        ("dividend_yield",     "Dividend Yield",   "Rendimento distribuído / preço",     "Peso 35% no score — normalizado (÷100 se > 1.0)"),
        ("dividend_growth_yoy","CAGR Dividendos",  "Crescimento anual dos dividendos",   "Peso 20% no score — calculado do histórico de dividendos"),
    ]

    lines.append("| Indicador | Preenchidos | Nulos | Cobertura | Barra | Observação |")
    lines.append("|---|---:|---:|---:|---|---|")
    for col, label, _, obs in campos_fii:
        cur.execute(f"""
            SELECT COUNT(*) FROM indicators i
            JOIN tickers t ON i.ticker_id=t.id
            WHERE t.asset_type='fii' AND i.{col} IS NOT NULL
        """)
        p = cur.fetchone()[0]
        nulos = n_fiis - p
        pct = p / n_fiis * 100
        bar = pct_bar(pct, 15)
        status = "✅" if pct >= 80 else ("⚠️" if pct >= 40 else "❌")
        lines.append(f"| **{label}** | {p} | {nulos} | {pct:.1f}% | `{bar}` {status} | {obs} |")

    # ── TOP 20 AÇÕES ───────────────────────────────────────────────────────
    h("5. Top 20 Ações por Score")

    cur.execute("""
        SELECT t.symbol, t.sector, i.score, i.score_label,
               i.roe, i.pe_ratio, i.pb_ratio, i.dividend_yield,
               i.net_income_growth_yoy, i.debt_ebitda, i.ev_ebitda
        FROM indicators i JOIN tickers t ON i.ticker_id=t.id
        WHERE t.asset_type='stock' AND i.score IS NOT NULL
        ORDER BY i.score DESC LIMIT 20
    """)
    lines.append("| Ticker | Score | Label | ROE | P/L | P/VP | DY | CAGR Lucro | D/EBITDA |")
    lines.append("|---|---:|---|---:|---:|---:|---:|---:|---:|")
    for r in cur.fetchall():
        roe  = f"{r['roe']*100:.1f}%"   if r['roe']                  else "—"
        pe   = f"{r['pe_ratio']:.1f}"   if r['pe_ratio']              else "—"
        pb   = f"{r['pb_ratio']:.2f}"   if r['pb_ratio']              else "—"
        dy   = f"{r['dividend_yield']*100:.1f}%" if r['dividend_yield'] else "—"
        cagr = f"{r['net_income_growth_yoy']*100:.1f}%" if r['net_income_growth_yoy'] else "—"
        de   = f"{r['debt_ebitda']:.2f}" if r['debt_ebitda']          else "—"
        lines.append(f"| **{r['symbol']}** | {r['score']:.1f} | {r['score_label']} | {roe} | {pe} | {pb} | {dy} | {cagr} | {de} |")

    # ── TOP 20 FIIs ────────────────────────────────────────────────────────
    h("6. Top 20 FIIs por Score")

    cur.execute("""
        SELECT t.symbol, i.score, i.score_label,
               i.pb_ratio, i.dividend_yield, i.dividend_growth_yoy, i.pe_ratio,
               f.current_price
        FROM indicators i
        JOIN tickers t ON i.ticker_id=t.id
        JOIN financial_data f ON f.ticker_id=t.id
        WHERE t.asset_type='fii' AND i.score IS NOT NULL
        ORDER BY i.score DESC LIMIT 20
    """)
    lines.append("| Ticker | Score | Label | P/VP | DY | CAGR DY | P/L | Preço |")
    lines.append("|---|---:|---|---:|---:|---:|---:|---:|")
    for r in cur.fetchall():
        pb   = f"{r['pb_ratio']:.2f}"   if r['pb_ratio']              else "—"
        dy   = f"{r['dividend_yield']*100:.1f}%" if r['dividend_yield'] else "—"
        cagr = f"{r['dividend_growth_yoy']*100:.1f}%" if r['dividend_growth_yoy'] else "—"
        pe   = f"{r['pe_ratio']:.1f}"   if r['pe_ratio']              else "—"
        preco= f"R$ {r['current_price']:.2f}" if r['current_price']   else "—"
        lines.append(f"| **{r['symbol']}** | {r['score']:.1f} | {r['score_label']} | {pb} | {dy} | {cagr} | {pe} | {preco} |")

    # ── BOTTOM 10 AÇÕES ────────────────────────────────────────────────────
    h("7. Bottom 10 Ações por Score")

    cur.execute("""
        SELECT t.symbol, t.sector, i.score, i.score_label,
               i.roe, i.pe_ratio, i.dividend_yield
        FROM indicators i JOIN tickers t ON i.ticker_id=t.id
        WHERE t.asset_type='stock' AND i.score IS NOT NULL
        ORDER BY i.score ASC LIMIT 10
    """)
    lines.append("| Ticker | Setor | Score | Label | ROE | P/L | DY |")
    lines.append("|---|---|---:|---|---:|---:|---:|")
    for r in cur.fetchall():
        roe = f"{r['roe']*100:.1f}%" if r['roe'] else "—"
        pe  = f"{r['pe_ratio']:.1f}" if r['pe_ratio'] else "—"
        dy  = f"{r['dividend_yield']*100:.1f}%" if r['dividend_yield'] else "—"
        setor = (r['sector'] or "—")[:30]
        lines.append(f"| **{r['symbol']}** | {setor} | {r['score']:.1f} | {r['score_label']} | {roe} | {pe} | {dy} |")

    # ── INATIVOS ───────────────────────────────────────────────────────────
    h("8. Tickers Inativos")

    lines.append(f"> Total: **{inativos} tickers inativos**\n")

    cur.execute("""
        SELECT reason, asset_type, COUNT(*) as n
        FROM inactive_tickers
        GROUP BY reason, asset_type
        ORDER BY reason, asset_type
    """)
    lines.append("| Motivo | Tipo | Qtd |")
    lines.append("|---|---|---:|")
    motivos = {"sem_preco": "Sem preço de mercado", "sem_dados": "Sem dados financeiros"}
    for r in cur.fetchall():
        lines.append(f"| {motivos.get(r['reason'], r['reason'])} | {r['asset_type'] or '—'} | {r['n']} |")

    # ── PONTOS DE ATENÇÃO ──────────────────────────────────────────────────
    h("9. Pontos de Atenção")

    # Coleta dados para análise
    cur.execute("""
        SELECT COUNT(*) FROM indicators i JOIN tickers t ON i.ticker_id=t.id
        WHERE t.asset_type='stock' AND i.debt_ebitda IS NULL
    """)
    sem_debt_ebitda = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM indicators i JOIN tickers t ON i.ticker_id=t.id
        WHERE t.asset_type='stock' AND i.ev_ebitda IS NULL
    """)
    sem_ev_ebitda = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM indicators i JOIN tickers t ON i.ticker_id=t.id
        WHERE t.asset_type='fii' AND i.pb_ratio IS NULL
    """)
    sem_pvp_fii = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM indicators i JOIN tickers t ON i.ticker_id=t.id
        WHERE t.asset_type='fii' AND i.dividend_yield IS NULL
    """)
    sem_dy_fii = cur.fetchone()[0]

    lines.append("| # | Indicador | Impacto | Causa | Ação sugerida |")
    lines.append("|---|---|---|---|---|")
    lines.append(f"| 1 | **Dívida/EBITDA** ({sem_debt_ebitda} ações sem dado) | Peso 15% no score — usa neutro (50) | fundamentus não retorna EBITDA diretamente; derivação via EV/EV_EBITDA requer EV_EBITDA > 0 | Rodar `ensure_min_indicators` para tentar via yfinance |")
    lines.append(f"| 2 | **EV/EBITDA** ({sem_ev_ebitda} ações sem dado) | Peso 10% no score — usa neutro (50) | fundamentus retorna `000` (ausente) para a maioria | Limitação da fonte — sem alternativa direta |")
    lines.append(f"| 3 | **P/VP FIIs** ({sem_pvp_fii} FIIs sem dado) | Peso 30% no score — usa neutro (50) | yfinance não retorna `priceToBook` para a maioria dos FIIs BR | Calcular via `current_price / book_value_per_share` quando disponível |")
    lines.append(f"| 4 | **DY FIIs** ({sem_dy_fii} FIIs sem dado) | Peso 35% no score — usa neutro (50) | yfinance não retorna `dividendYield` para alguns FIIs | Calcular via `dividends_12m / current_price` do histórico |")
    lines.append(f"| 5 | **CAGR Lucro ações** (~{n_stocks - 277} ações sem dado) | Peso 15% no score — usa neutro (50) | Limitação do yfinance: ~44.7% das ações têm DRE histórico | Rodar `update_income_growth` mensalmente |")

    # ── RODAPÉ ────────────────────────────────────────────────────────────
    lines.append("\n---")
    lines.append(f"\n> Relatório gerado automaticamente por `backend/scripts/generate_report.py` em {now}.")
    lines.append("> Para atualizar: `python -m backend.scripts.generate_report`")

    conn.close()
    return "\n".join(lines)


def run(output: str = None) -> None:
    """Gera e salva o relatório."""
    content = generate_report()

    if output is None:
        # Salva em backend/reports/
        reports_dir = Path("backend/reports")
        if not reports_dir.exists():
            reports_dir = Path("reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        output = str(reports_dir / "relatorio_banco.md")

    Path(output).write_text(content, encoding="utf-8")
    print(f"✅ Relatório gerado: {output}")
    print(f"   {len(content.splitlines())} linhas | {len(content):,} caracteres")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gera relatório do banco em Markdown")
    parser.add_argument("--output", type=str, default=None, help="Caminho do arquivo .md de saída")
    args = parser.parse_args()
    run(output=args.output)
