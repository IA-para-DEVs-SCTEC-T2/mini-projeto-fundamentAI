"""
Classificação de tipo de ativo e detecção de inativos.

Responsabilidades:
- Determinar se um ticker é ação (stock) ou FII
- Detectar tickers inativos antes de coletar dados
- Gerar relatório de inativos

Regras de classificação (dois níveis):
1. Offline (por símbolo): ticker termina em 11 E não está na lista de units
2. Online (via yfinance): industryKey começa com "reit-" → FII confirmado

Critérios de inatividade:
- Preço de mercado zero ou ausente
- Sem qualquer indicador disponível (ROE, P/L, P/VP todos nulos)
- Sem dados financeiros básicos (net_income e total_equity nulos)
"""

import logging
import re
from datetime import datetime
from typing import Optional

import pandas as pd

from backend.db.models import ASSET_TYPE_FII, ASSET_TYPE_STOCK

logger = logging.getLogger(__name__)

# Padrão de ticker FII: exatamente 4 letras + 11
_FII_PATTERN = re.compile(r"^[A-Z]{4}11$")

# Units de empresas que terminam em 11 mas NÃO são FIIs.
# Critério definitivo: industryKey via yfinance NÃO começa com "reit-"
# Esta lista cobre os casos conhecidos para classificação offline (sem API).
_NOT_FII_UNITS: frozenset[str] = frozenset({
    # Energia elétrica
    "AESB11", "ALUP11", "CEPE11", "CMIG11", "COCE11", "CPFE11",
    "CPLE11", "EGIE11", "EKTR11", "EMAE11", "ENGI11", "ENMT11",
    "EQTL11", "ETER11", "EUCA11", "GEPA11", "GGBR11", "LIGT11",
    "NEOE11", "OMGE11", "SAPR11", "TAEE11", "TIET11", "TRPL11",
    # Financeiro / Bancos
    "ABCB11", "BPAC11", "BRBI11", "BRGE11", "BSLI11", "ITSA11",
    "SANB11", "WIZC11",
    # Papel e celulose
    "KLBN11", "SUZB11",
    # Real Estate empresas (não fundos) — industryKey = real-estate-services
    "IGTI11", "MEAL11", "PCAR11", "SOMA11", "MULT11", "BRPR11",
    # Outros setores
    "AALR11", "ABEV11", "AMAR11", "ATOM11", "BAHI11", "BBTG11",
    "BIDI11", "BMGB11", "BOAS11", "BPAN11", "BSEV11",
    "CALI11", "CBAV11", "CGAS11", "CGRA11", "CIEL11", "CLSC11",
    "CSRN11", "DASA11", "DEXP11", "DOHL11", "DTEX11",
    "EALT11", "EEEL11", "ELPL11", "EQPA11", "FESA11", "FHER11",
    "FIGE11", "FRAS11", "GFSA11", "GOAU11", "GPCP11", "GRND11",
    "HBOR11", "HETA11", "HGTX11", "IDVL11", "INEP11", "JBSS11",
    "JSLG11", "KEPL11", "LAME11", "LEVE11", "LIQO11", "LLIS11",
    "LOGN11", "LPSB11", "LREN11", "LUXM11", "MDIA11", "MGEL11",
    "MGLU11", "MILS11", "MOVI11", "MRFG11", "MRVE11", "MYPK11",
    "NATU11", "NEMO11", "NORD11", "NTCO11", "NUTR11", "ODPV11",
    "OFSA11", "OMGE11", "ORVR11", "PATI11", "PDGR11", "PETR11",
    "PINE11", "PMAM11", "PNVL11", "POMO11", "POSI11", "PRIO11",
    "PTBL11", "PTNT11", "QUAL11", "RADL11", "RAIL11", "RAPT11",
    "RCSL11", "RDNI11", "RENT11", "RLOG11", "RNEW11", "ROMI11",
    "RSID11", "SBSP11", "SCAR11", "SEER11", "SEQL11", "SGPS11",
    "SHOW11", "SHUL11", "SLCE11", "SMLS11", "SMTO11", "SOND11",
    "SQIA11", "STBP11", "SULA11", "TASA11", "TCNO11", "TGMA11",
    "TIMS11", "TPIS11", "TRIS11", "TUPY11", "UCAS11", "UGPA11",
    "UNIP11", "USIM11", "VALE11", "VBBR11", "VIVA11", "VIVT11",
    "VLID11", "VULC11", "WEGE11", "WEST11", "WHRL11", "WIZS11",
    "YDUQ11",
})

# Razões de inatividade
REASON_NO_PRICE = "sem_preco"
REASON_NO_DATA = "sem_dados"
REASON_DELISTED = "deslistado"


def classify_asset_type(symbol: str) -> str:
    """
    Classificação offline por símbolo (sem chamada de API).

    Regras:
    1. Símbolo deve ter exatamente 4 letras + "11"
    2. Não pode estar na lista _NOT_FII_UNITS (units de empresas conhecidas)

    Para classificação definitiva use is_real_fii_via_yfinance().

    Returns:
        "fii" (candidato a FII) ou "stock".
    """
    symbol = symbol.upper().strip()
    if _FII_PATTERN.match(symbol) and symbol not in _NOT_FII_UNITS:
        return ASSET_TYPE_FII
    return ASSET_TYPE_STOCK


def is_real_fii_via_yfinance(symbol: str) -> bool:
    """
    Confirma via yfinance se um ticker é realmente um FII.

    Critério definitivo: industryKey começa com "reit-"
    Fallback: longName contém "Fundo" e "Imobiliario" (para FIIs sem industryKey)

    Args:
        symbol: Símbolo do ativo (ex: HGLG11).

    Returns:
        True se for FII real, False caso contrário.
    """
    try:
        import yfinance as yf
        ticker_sa = symbol.upper().strip()
        if not ticker_sa.endswith(".SA"):
            ticker_sa += ".SA"
        info = yf.Ticker(ticker_sa).info
        industry_key = (info.get("industryKey") or "").lower()
        if industry_key.startswith("reit-"):
            return True
        # Fallback: nome contém indicadores de fundo imobiliário
        long_name = (info.get("longName") or "").lower()
        if "fundo" in long_name and ("imobili" in long_name or "fii" in long_name):
            return True
        return False
    except Exception:
        return False


def is_inactive(
    symbol: str,
    current_price: Optional[float],
    net_income: Optional[float] = None,
    total_equity: Optional[float] = None,
    roe: Optional[float] = None,
    pe_ratio: Optional[float] = None,
    pb_ratio: Optional[float] = None,
) -> tuple[bool, str]:
    """
    Verifica se um ticker deve ser considerado inativo.

    Critérios (qualquer um é suficiente):
    1. Preço zero ou ausente
    2. Sem nenhum indicador (ROE, P/L, P/VP todos nulos) E sem dados financeiros

    Args:
        symbol: Símbolo do ativo.
        current_price: Preço atual de mercado.
        net_income: Lucro líquido (pode ser None para FIIs).
        total_equity: Patrimônio líquido.
        roe: ROE calculado.
        pe_ratio: P/L calculado.
        pb_ratio: P/VP calculado.

    Returns:
        (is_inactive, reason): Tupla com flag e motivo.
    """
    # Critério 1: sem preço
    if current_price is None or current_price == 0:
        return True, REASON_NO_PRICE

    # Critério 2: sem nenhum indicador E sem dados financeiros básicos
    has_any_indicator = any(v is not None for v in [roe, pe_ratio, pb_ratio])
    has_financial_data = any(v is not None for v in [net_income, total_equity])

    if not has_any_indicator and not has_financial_data:
        return True, REASON_NO_DATA

    return False, ""


def generate_inactive_report(
    inactive_list: list[dict],
    output_csv: str = None,
) -> pd.DataFrame:
    """
    Gera relatório de tickers inativos em CSV.

    Args:
        inactive_list: Lista de dicionários com dados dos inativos.
        output_csv: Caminho do arquivo CSV. Padrão: backend/reports/relatorio_inativos.csv

    Returns:
        DataFrame com os dados dos inativos.
    """
    from backend.scripts._report_utils import report_path
    if output_csv is None:
        output_csv = report_path("relatorio_inativos.csv")

    if not inactive_list:
        logger.info("Nenhum ticker inativo encontrado.")
        return pd.DataFrame()

    df = pd.DataFrame(inactive_list)

    # Ordena por setor e símbolo
    if "sector" in df.columns and "symbol" in df.columns:
        df = df.sort_values(["sector", "symbol"], na_position="last")

    df.to_csv(output_csv, index=False, encoding="utf-8-sig")

    logger.info("Relatório de inativos exportado: %s (%d tickers)", output_csv, len(df))

    # Resumo no console
    print("\n" + "=" * 60)
    print("RELATÓRIO DE TICKERS INATIVOS")
    print("=" * 60)
    print(f"Total de inativos: {len(df)}")

    if "reason" in df.columns:
        print("\nPor motivo:")
        for reason, count in df["reason"].value_counts().items():
            labels = {
                REASON_NO_PRICE: "Sem preço de mercado",
                REASON_NO_DATA: "Sem dados financeiros",
                REASON_DELISTED: "Deslistado",
            }
            print(f"  {labels.get(reason, reason)}: {count}")

    if "sector" in df.columns:
        print("\nPor setor (top 10):")
        for sector, count in df["sector"].value_counts(dropna=False).head(10).items():
            print(f"  {str(sector):<40}: {count}")

    print(f"\nCSV salvo em: {output_csv}")
    print("=" * 60)

    return df


def persist_inactive_tickers(db, inactive_list: list[dict]) -> int:
    """
    Persiste tickers inativos na tabela InactiveTicker.

    Args:
        db: Sessão do banco de dados.
        inactive_list: Lista de dicionários com dados dos inativos.
            Campos esperados: symbol, name, sector, asset_type, b3_type, reason, last_price

    Returns:
        Número de registros inseridos/atualizados.
    """
    from backend.db.models import InactiveTicker

    count = 0
    for item in inactive_list:
        symbol = item.get("symbol", "").upper()
        if not symbol:
            continue

        # Classifica o tipo se não informado
        asset_type = item.get("asset_type") or classify_asset_type(symbol)

        existing = db.query(InactiveTicker).filter(
            InactiveTicker.symbol == symbol
        ).first()

        if existing:
            existing.reason = item.get("reason")
            existing.last_price = item.get("last_price")
            existing.asset_type = asset_type
            existing.last_checked_at = datetime.utcnow()
        else:
            inactive = InactiveTicker(
                symbol=symbol,
                name=item.get("name"),
                sector=item.get("sector"),
                asset_type=asset_type,
                b3_type=item.get("b3_type"),
                reason=item.get("reason"),
                last_price=item.get("last_price"),
            )
            db.add(inactive)
            count += 1

    db.commit()
    return count


def get_inactive_symbols(db) -> set[str]:
    """
    Retorna o conjunto de símbolos inativos do banco.

    Args:
        db: Sessão do banco de dados.

    Returns:
        Set de símbolos inativos (ex: {"ABCB3", "BPNM3"}).
    """
    from backend.db.models import InactiveTicker

    rows = db.query(InactiveTicker.symbol).all()
    return {row.symbol for row in rows}
