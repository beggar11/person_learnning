import pytest
from fastapi.testclient import TestClient
from config import BASE_DIR
from database import init_db, get_db

@pytest.fixture
def app():
    import main
    test_db = BASE_DIR / "test_kb.db"
    import config
    config.DB_PATH = test_db
    init_db()
    yield main.app
    if test_db.exists():
        test_db.unlink()

@pytest.fixture
def client(app):
    return TestClient(app)

@pytest.fixture
def db(app):
    conn = get_db()
    yield conn
    conn.close()
