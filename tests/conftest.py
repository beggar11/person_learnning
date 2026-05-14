import pytest
from fastapi.testclient import TestClient
from config import BASE_DIR
from database import _connect, init_db

@pytest.fixture
def app():
    test_db = BASE_DIR / "test_kb.db"
    import config
    config.DB_PATH = test_db
    import main
    init_db()
    yield main.app
    if test_db.exists():
        test_db.unlink()

@pytest.fixture
def client(app):
    return TestClient(app)

@pytest.fixture
def db(app):
    conn = _connect()
    yield conn
    conn.close()
