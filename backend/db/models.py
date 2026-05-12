"""
Modelos SQLAlchemy para o FundamentAI.

Tabelas:
- Ticker: ações e FIIs cadastrados no sistema
- FinancialData: dados financeiros brutos coletados (DRE, Balanço)
- Indicators: indicadores fundamentalistas calculados
- Analysis: análises geradas pela LLM (veredito, score, etc.)
"""

import os
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fundamentai.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class Ticker(Base):
    """Ações e FIIs cadastrados no sistema."""

    __tablename__ = "tickers"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=True)
    sector = Column(String(100), nullable=True)
    segment = Column(String(100), nullable=True)
    asset_type = Column(String(20), nullable=True)  # "stock" | "fii"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    financial_data = relationship("FinancialData", back_populates="ticker", cascade="all, delete-orphan")
    indicators = relationship("Indicators", back_populates="ticker", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="ticker", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Ticker(symbol={self.symbol}, name={self.name})>"


class FinancialData(Base):
    """Dados financeiros brutos coletados (DRE, Balanço Patrimonial, cotação)."""

    __tablename__ = "financial_data"

    id = Column(Integer, primary_key=True, index=True)
    ticker_id = Column(Integer, ForeignKey("tickers.id"), nullable=False, index=True)
    reference_date = Column(DateTime, nullable=False, index=True)

    # Cotação
    current_price = Column(Float, nullable=True)
    market_cap = Column(Float, nullable=True)

    # DRE (Demonstração do Resultado do Exercício)
    revenue = Column(Float, nullable=True)           # Receita líquida
    net_income = Column(Float, nullable=True)        # Lucro líquido
    ebitda = Column(Float, nullable=True)            # EBITDA
    gross_profit = Column(Float, nullable=True)      # Lucro bruto

    # Balanço Patrimonial
    total_assets = Column(Float, nullable=True)      # Ativo total
    total_equity = Column(Float, nullable=True)      # Patrimônio líquido
    total_debt = Column(Float, nullable=True)        # Dívida total
    net_debt = Column(Float, nullable=True)          # Dívida líquida
    invested_capital = Column(Float, nullable=True)  # Capital investido

    # Dados brutos em JSON (para flexibilidade)
    raw_data = Column(Text, nullable=True)

    collected_at = Column(DateTime, default=datetime.utcnow)

    ticker = relationship("Ticker", back_populates="financial_data")

    def __repr__(self) -> str:
        return f"<FinancialData(ticker_id={self.ticker_id}, date={self.reference_date})>"


class Indicators(Base):
    """Indicadores fundamentalistas calculados."""

    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True, index=True)
    ticker_id = Column(Integer, ForeignKey("tickers.id"), nullable=False, index=True)
    reference_date = Column(DateTime, nullable=False, index=True)

    # Rentabilidade
    roe = Column(Float, nullable=True)               # Retorno sobre Patrimônio (%)
    roic = Column(Float, nullable=True)              # Retorno sobre Capital Investido (%)
    net_margin = Column(Float, nullable=True)        # Margem líquida (%)

    # Endividamento
    debt_ebitda = Column(Float, nullable=True)       # Dívida líquida / EBITDA

    # Valuation
    pe_ratio = Column(Float, nullable=True)          # P/L (Preço / Lucro)
    pb_ratio = Column(Float, nullable=True)          # P/VP (Preço / Valor Patrimonial)

    # Crescimento (YoY)
    revenue_growth_yoy = Column(Float, nullable=True)    # Crescimento de receita (%)
    net_income_growth_yoy = Column(Float, nullable=True) # Crescimento de lucro (%)

    # Score calculado
    score = Column(Float, nullable=True)             # Score fundamentalista (0-100)
    score_label = Column(String(20), nullable=True)  # Excelente | Bom | Regular | Fraco

    calculated_at = Column(DateTime, default=datetime.utcnow)

    ticker = relationship("Ticker", back_populates="indicators")

    def __repr__(self) -> str:
        return f"<Indicators(ticker_id={self.ticker_id}, score={self.score})>"


class Analysis(Base):
    """Análises geradas pela LLM (Anthropic Claude)."""

    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    ticker_id = Column(Integer, ForeignKey("tickers.id"), nullable=False, index=True)

    # Resultado da análise
    verdict = Column(String(50), nullable=True)          # Ex: "Positivo", "Neutro", "Negativo"
    score = Column(Float, nullable=True)                 # Score 0-100
    confidence_level = Column(String(20), nullable=True) # "Alto" | "Médio" | "Baixo"

    # Conteúdo estruturado
    positive_points = Column(Text, nullable=True)        # JSON array de pontos positivos
    negative_points = Column(Text, nullable=True)        # JSON array de pontos negativos
    indicators_explanation = Column(Text, nullable=True) # Explicação dos indicadores
    conclusion = Column(Text, nullable=True)             # Conclusão geral
    moment_suggestion = Column(Text, nullable=True)      # Sugestão de momento (não recomendação)

    # Metadados da geração
    model_used = Column(String(50), nullable=True)       # claude-sonnet-4-5 | claude-haiku-4-5
    prompt_version = Column(String(20), nullable=True)   # Versão do template de prompt
    raw_response = Column(Text, nullable=True)           # Resposta bruta da LLM

    generated_at = Column(DateTime, default=datetime.utcnow)

    ticker = relationship("Ticker", back_populates="analyses")

    def __repr__(self) -> str:
        return f"<Analysis(ticker_id={self.ticker_id}, verdict={self.verdict}, score={self.score})>"


def create_tables() -> None:
    """Cria todas as tabelas no banco de dados."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Dependency para injeção de sessão do banco nas rotas FastAPI.

    Uso:
        @app.get("/example")
        def example(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
