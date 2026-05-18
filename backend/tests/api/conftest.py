"""
Fixtures compartilhadas para testes de API.

Configura banco de dados SQLite em memória para isolar os testes
da API sem depender de banco real ou arquivos externos.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.db.models import Base, get_db
from backend.api.main import app


@pytest.fixture(scope="session")
def test_engine():
    """Engine SQLite em memória para toda a sessão de testes."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Sessão de banco isolada por teste, com rollback automático."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="session", autouse=True)
def override_db(test_engine):
    """
    Substitui a dependência get_db da FastAPI pelo banco em memória
    para toda a sessão de testes.
    """
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )

    def _get_test_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()
