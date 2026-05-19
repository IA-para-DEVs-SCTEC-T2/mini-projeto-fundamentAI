"""
Modelos SQLAlchemy para o FundamentAI.

Tabelas:
- Ticker: ações e FIIs cadastrados no sistema
- FinancialData: dados financeiros brutos coletados (DRE, Balanço, dividendos)
- Indicators: indicadores fundamentalistas calculados (ações e FIIs)
- Analysis: análises geradas pela LLM (veredito, score, etc.)
- InactiveTicker: tickers inativos mapeados e excluídos da análise
"""

import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import (
    Boolean,
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

# Carrega o .env da raiz do projeto (funciona independente do diretório de execução)
_ROOT_DIR = Path(__file__).resolve().parents[3]  # mini-projeto-equipe08/
load_dotenv(_ROOT_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fundamentai.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Constantes de tipo de ativo
# ---------------------------------------------------------------------------

ASSET_TYPE_STOCK = "stock"   # Ação (empresa da B3)
ASSET_TYPE_FII = "fii"       # Fundo de Investimento Imobiliário


class Ticker(Base):
    """Ações e FIIs ativos cadastrados no sistema."""

    __tablename__ = "tickers"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=True)
    sector = Column(String(100), nullable=True)
    segment = Column(String(100), nullable=True)

    # Tipo normalizado: "stock" | "fii"
    asset_type = Column(String(10), nullable=False, default=ASSET_TYPE_STOCK, index=True)

    # Tipo original da B3 (ex: "ON NM", "PN", "UNT N2")
    b3_type = Column(String(30), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    financial_data = relationship("FinancialData", back_populates="ticker", cascade="all, delete-orphan")
    indicators = relationship("Indicators", back_populates="ticker", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="ticker", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Ticker(symbol={self.symbol}, type={self.asset_type})>"


class InactiveTicker(Base):
    """
    Tickers inativos mapeados e excluídos da análise.

    Critério de inatividade:
    - Preço de mercado zero ou ausente
    - Sem qualquer indicador disponível (ROE, P/L, P/VP todos nulos)
    - Sem dados financeiros (net_income, total_equity nulos)
    """

    __tablename__ = "inactive_tickers"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=True)
    sector = Column(String(100), nullable=True)

    # Tipo do ativo: "stock" | "fii"
    asset_type = Column(String(10), nullable=True, index=True)

    # Tipo original da B3 (ex: "ON NM", "PN", "DR3")
    b3_type = Column(String(30), nullable=True)

    # Motivo da inatividade
    reason = Column(String(100), nullable=True)  # "sem_preco" | "sem_dados" | "deslistado"

    # Dados disponíveis no momento da classificação
    last_price = Column(Float, nullable=True)
    last_checked_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<InactiveTicker(symbol={self.symbol}, type={self.asset_type}, reason={self.reason})>"


class FinancialData(Base):
    """
    Dados financeiros brutos coletados.

    Ações: DRE, Balanço Patrimonial, cotação (via fundamentus + yfinance)
    FIIs: cotação, dividendos, P/VP (via yfinance)
    """

    __tablename__ = "financial_data"

    id = Column(Integer, primary_key=True, index=True)
    ticker_id = Column(Integer, ForeignKey("tickers.id"), nullable=False, index=True)
    reference_date = Column(DateTime, nullable=False, index=True)

    # --- Campos comuns (ações e FIIs) ---
    current_price = Column(Float, nullable=True)
    market_cap = Column(Float, nullable=True)

    # --- Campos de ações ---
    revenue = Column(Float, nullable=True)           # Receita líquida
    net_income = Column(Float, nullable=True)        # Lucro líquido
    ebitda = Column(Float, nullable=True)            # EBITDA
    gross_profit = Column(Float, nullable=True)      # Lucro bruto
    total_assets = Column(Float, nullable=True)      # Ativo total
    total_equity = Column(Float, nullable=True)      # Patrimônio líquido
    total_debt = Column(Float, nullable=True)        # Dívida total
    net_debt = Column(Float, nullable=True)          # Dívida líquida
    invested_capital = Column(Float, nullable=True)  # Capital investido
    enterprise_value = Column(Float, nullable=True)  # EV (Valor da firma)

    # --- Campos de FIIs ---
    book_value_per_share = Column(Float, nullable=True)  # VPA (Valor Patrimonial por Cota)
    shares_outstanding = Column(Float, nullable=True)    # Número de cotas
    dividend_yield = Column(Float, nullable=True)        # DY anual (%)
    last_dividend = Column(Float, nullable=True)         # Último dividendo pago
    last_dividend_date = Column(DateTime, nullable=True) # Data do último dividendo
    dividends_12m = Column(Float, nullable=True)         # Total de dividendos nos últimos 12m
    dividend_growth_yoy = Column(Float, nullable=True)   # Crescimento de dividendos YoY (%)

    # Dados brutos em JSON (para flexibilidade futura)
    raw_data = Column(Text, nullable=True)

    collected_at = Column(DateTime, default=datetime.utcnow)

    ticker = relationship("Ticker", back_populates="financial_data")

    def __repr__(self) -> str:
        return f"<FinancialData(ticker_id={self.ticker_id}, date={self.reference_date})>"


class Indicators(Base):
    """
    Indicadores fundamentalistas calculados.

    Ações: ROE, ROIC, margem líquida, dívida/EBITDA, P/L, P/VP, EV/EBITDA,
           dividend yield, crescimento de lucro YoY
    FIIs:  P/VP, P/L, dividend yield, crescimento de dividendos YoY

    Score e label são iguais para ambos os tipos (output unificado).
    """

    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True, index=True)
    ticker_id = Column(Integer, ForeignKey("tickers.id"), nullable=False, index=True)
    reference_date = Column(DateTime, nullable=False, index=True)

    # --- Indicadores de ações ---
    roe = Column(Float, nullable=True)               # Retorno sobre Patrimônio (decimal)
    roic = Column(Float, nullable=True)              # Retorno sobre Capital Investido (decimal)
    net_margin = Column(Float, nullable=True)        # Margem líquida (decimal)
    debt_ebitda = Column(Float, nullable=True)       # Dívida líquida / EBITDA
    ev_ebitda = Column(Float, nullable=True)         # EV / EBITDA
    net_income_growth_yoy = Column(Float, nullable=True)  # Crescimento de lucro YoY (decimal)

    # --- Indicadores comuns (ações e FIIs) ---
    pe_ratio = Column(Float, nullable=True)          # P/L (Preço / Lucro)
    pb_ratio = Column(Float, nullable=True)          # P/VP (Preço / Valor Patrimonial)
    dividend_yield = Column(Float, nullable=True)    # Dividend Yield (decimal)

    # --- Indicadores de FIIs ---
    dividend_growth_yoy = Column(Float, nullable=True)  # Crescimento de dividendos YoY (decimal)

    # --- Crescimento de receita (ações) ---
    revenue_growth_yoy = Column(Float, nullable=True)   # CAGR receita (decimal)

    # --- Score unificado (mesmo output para ações e FIIs) ---
    score = Column(Float, nullable=True)             # Score 0-100
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

    verdict = Column(String(50), nullable=True)
    score = Column(Float, nullable=True)
    confidence_level = Column(String(20), nullable=True)
    positive_points = Column(Text, nullable=True)
    negative_points = Column(Text, nullable=True)
    indicators_explanation = Column(Text, nullable=True)
    conclusion = Column(Text, nullable=True)
    moment_suggestion = Column(Text, nullable=True)
    model_used = Column(String(50), nullable=True)
    prompt_version = Column(String(20), nullable=True)
    raw_response = Column(Text, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)

    ticker = relationship("Ticker", back_populates="analyses")

    def __repr__(self) -> str:
        return f"<Analysis(ticker_id={self.ticker_id}, verdict={self.verdict})>"


def create_tables() -> None:
    """Cria todas as tabelas no banco de dados."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency para injeção de sessão do banco nas rotas FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
