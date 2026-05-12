"""
Repository pattern para acesso ao banco de dados.

Abstrai as operações CRUD para cada entidade, mantendo a lógica de
persistência separada das rotas da API e do ETL.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from backend.db.models import Analysis, FinancialData, Indicators, Ticker


# ---------------------------------------------------------------------------
# Ticker
# ---------------------------------------------------------------------------


class TickerRepository:
    """Operações CRUD para a entidade Ticker."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_symbol(self, symbol: str) -> Optional[Ticker]:
        """Busca um ticker pelo símbolo (ex: PETR4)."""
        return self.db.query(Ticker).filter(Ticker.symbol == symbol.upper()).first()

    def get_all(self) -> list[Ticker]:
        """Retorna todos os tickers cadastrados."""
        return self.db.query(Ticker).all()

    def create(
        self,
        symbol: str,
        name: Optional[str] = None,
        sector: Optional[str] = None,
        segment: Optional[str] = None,
        asset_type: Optional[str] = "stock",
    ) -> Ticker:
        """Cria um novo ticker."""
        ticker = Ticker(
            symbol=symbol.upper(),
            name=name,
            sector=sector,
            segment=segment,
            asset_type=asset_type,
        )
        self.db.add(ticker)
        self.db.commit()
        self.db.refresh(ticker)
        return ticker

    def get_or_create(self, symbol: str, **kwargs) -> tuple[Ticker, bool]:
        """
        Retorna o ticker existente ou cria um novo.

        Returns:
            (ticker, created): ticker e flag indicando se foi criado agora.
        """
        ticker = self.get_by_symbol(symbol)
        if ticker:
            return ticker, False
        ticker = self.create(symbol, **kwargs)
        return ticker, True

    def update(self, ticker: Ticker, **kwargs) -> Ticker:
        """Atualiza campos de um ticker existente."""
        for key, value in kwargs.items():
            if hasattr(ticker, key):
                setattr(ticker, key, value)
        ticker.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(ticker)
        return ticker

    def delete(self, ticker: Ticker) -> None:
        """Remove um ticker e todos os dados associados (cascade)."""
        self.db.delete(ticker)
        self.db.commit()


# ---------------------------------------------------------------------------
# FinancialData
# ---------------------------------------------------------------------------


class FinancialDataRepository:
    """Operações CRUD para dados financeiros brutos."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_latest(self, ticker_id: int) -> Optional[FinancialData]:
        """Retorna o registro mais recente de dados financeiros para um ticker."""
        return (
            self.db.query(FinancialData)
            .filter(FinancialData.ticker_id == ticker_id)
            .order_by(FinancialData.reference_date.desc())
            .first()
        )

    def get_history(self, ticker_id: int, limit: int = 20) -> list[FinancialData]:
        """Retorna o histórico de dados financeiros para um ticker."""
        return (
            self.db.query(FinancialData)
            .filter(FinancialData.ticker_id == ticker_id)
            .order_by(FinancialData.reference_date.desc())
            .limit(limit)
            .all()
        )

    def create(self, ticker_id: int, reference_date: datetime, **kwargs) -> FinancialData:
        """Cria um novo registro de dados financeiros."""
        financial_data = FinancialData(
            ticker_id=ticker_id,
            reference_date=reference_date,
            **kwargs,
        )
        self.db.add(financial_data)
        self.db.commit()
        self.db.refresh(financial_data)
        return financial_data

    def upsert(self, ticker_id: int, reference_date: datetime, **kwargs) -> FinancialData:
        """
        Cria ou atualiza dados financeiros para uma data de referência.
        Evita duplicatas para o mesmo ticker + data.
        """
        existing = (
            self.db.query(FinancialData)
            .filter(
                FinancialData.ticker_id == ticker_id,
                FinancialData.reference_date == reference_date,
            )
            .first()
        )
        if existing:
            for key, value in kwargs.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        return self.create(ticker_id, reference_date, **kwargs)


# ---------------------------------------------------------------------------
# Indicators
# ---------------------------------------------------------------------------


class IndicatorsRepository:
    """Operações CRUD para indicadores fundamentalistas calculados."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_latest(self, ticker_id: int) -> Optional[Indicators]:
        """Retorna os indicadores mais recentes para um ticker."""
        return (
            self.db.query(Indicators)
            .filter(Indicators.ticker_id == ticker_id)
            .order_by(Indicators.reference_date.desc())
            .first()
        )

    def get_history(self, ticker_id: int, limit: int = 20) -> list[Indicators]:
        """Retorna o histórico de indicadores para um ticker."""
        return (
            self.db.query(Indicators)
            .filter(Indicators.ticker_id == ticker_id)
            .order_by(Indicators.reference_date.desc())
            .limit(limit)
            .all()
        )

    def create(self, ticker_id: int, reference_date: datetime, **kwargs) -> Indicators:
        """Cria um novo registro de indicadores."""
        indicators = Indicators(
            ticker_id=ticker_id,
            reference_date=reference_date,
            **kwargs,
        )
        self.db.add(indicators)
        self.db.commit()
        self.db.refresh(indicators)
        return indicators

    def upsert(self, ticker_id: int, reference_date: datetime, **kwargs) -> Indicators:
        """Cria ou atualiza indicadores para uma data de referência."""
        existing = (
            self.db.query(Indicators)
            .filter(
                Indicators.ticker_id == ticker_id,
                Indicators.reference_date == reference_date,
            )
            .first()
        )
        if existing:
            for key, value in kwargs.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        return self.create(ticker_id, reference_date, **kwargs)


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------


class AnalysisRepository:
    """Operações CRUD para análises geradas pela LLM."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_latest(self, ticker_id: int) -> Optional[Analysis]:
        """Retorna a análise mais recente para um ticker."""
        return (
            self.db.query(Analysis)
            .filter(Analysis.ticker_id == ticker_id)
            .order_by(Analysis.generated_at.desc())
            .first()
        )

    def get_history(self, ticker_id: int, limit: int = 10) -> list[Analysis]:
        """Retorna o histórico de análises para um ticker."""
        return (
            self.db.query(Analysis)
            .filter(Analysis.ticker_id == ticker_id)
            .order_by(Analysis.generated_at.desc())
            .limit(limit)
            .all()
        )

    def create(self, ticker_id: int, **kwargs) -> Analysis:
        """Cria um novo registro de análise."""
        analysis = Analysis(ticker_id=ticker_id, **kwargs)
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis
