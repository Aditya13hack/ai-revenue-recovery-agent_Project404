import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import backend.database.connection as conn
from backend.database.models import Base

@pytest.fixture(scope="session", autouse=True)
def test_db():
    """Redirect all test DB operations to an isolated test database."""
    test_db_path = "test_suite_isolated.db"
    test_engine = create_engine(
        f"sqlite:///{test_db_path}",
        echo=False,
        connect_args={"check_same_thread": False},
    )
    test_sessionmaker = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)

    orig_engine = conn.engine
    orig_sessionmaker = conn.SessionLocal

    conn.engine = test_engine
    conn.SessionLocal = test_sessionmaker
    conn.init_db()

    yield test_engine

    conn.engine = orig_engine
    conn.SessionLocal = orig_sessionmaker
    test_engine.dispose()
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except Exception:
            pass
