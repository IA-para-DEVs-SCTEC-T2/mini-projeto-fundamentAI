"""
Classificação de tipo de ativo e detecção de inativos.

Responsabilidades:
- Determinar se um ticker é ação (stock) ou FII
- Detectar tickers inativos antes de coletar dados
- Gerar relatório de inativos

Regras de classificação:
- FII: ticker termina em 11 (ex: HGLG11, XPML11, KNRI11)
- Ação: todos os demais (ON, PN, UNT, etc.)

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

# Padrão de ticker FII: 4 letras + 11
_FII_PATTERN = re.compile(r"^[A-Z]{4}11$")

# Razões de inatividade
REASON_NO_PRICE = "sem_preco"
REASON_NO_DATA = "sem_dados"
REASON_DELISTED = "deslistado"


def classify_asset_type(symbol: str) -> str:
    """
    Determina o tipo de ativo com base no símbolo.

    Args:
        symbol: Símbolo do ativo (ex: PETR4, HGLG11).

    Returns:
        "fii" para Fundos Imobiliários, "stock" para ações.

    Exemplos:
        >>> classify_asset_type("HGLG11")
        "fii"
        >>> classify_asset_type("PETR4")
        "stock"
        >>> classify_asset_type("MXRF11")
        "fii"
    """
    symbol = symbol.upper().strip()
    if _FII_PATTERN.match(symbol):
        return ASSET_TYPE_FII
    return ASSET_TYPE_STOCK


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
