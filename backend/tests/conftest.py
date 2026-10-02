import os
import pytest
from fastapi.testclient import TestClient

# Force setting environment to 'testing' and configuring test database name
os.environ["ENV"] = "testing"
os.environ["MONGODB_DATABASE"] = "phishing_detection_test_db"

from app.config import settings
from app.database.connection import db_manager
from app.database.collections import init_collections_and_indexes

# Check database availability dynamically before test execution
def check_db_connection() -> bool:
    try:
        import pymongo
        # Short timeout (2 seconds) to check if MongoDB is active
        client = pymongo.MongoClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=2000,
            connectTimeoutMS=2000
        )
        client.admin.command("ping")
        client.close()
        return True
    except Exception:
        return False

DB_AVAILABLE = check_db_connection()

@pytest.fixture(scope="session", autouse=True)
def test_db_lifecycle():
    """
    Manages connection to the test MongoDB database, initial index building,
    and drops the test database during teardown.
    """
    if not DB_AVAILABLE:
        print("\n[Warning] MongoDB connection check failed. Skipping database setup lifecycle.")
        yield None
        return

    connected = False
    try:
        db_manager.connect()
        init_collections_and_indexes()
        connected = True
    except Exception as e:
        print(f"\n[Warning] Database connection failed: {str(e)}")

    yield db_manager

    # Drop test database upon completion of the test suite (only if test database is targeted)
    if connected:
        target_db = settings.MONGODB_DATABASE
        if "test" in target_db.lower() or target_db.endswith("_test_db"):
            try:
                db_manager.client.drop_database(target_db)
                print(f"\n[Info] Dropped test database: '{target_db}' successfully.")
            except Exception as e:
                print(f"\n[Warning] Could not drop test database '{target_db}': {str(e)}")
        
        # Shut down pymongo client pool
        db_manager.close()

@pytest.fixture
def require_db():
    """
    Fixture that skips tests when MongoDB is not available in the test environment.
    """
    if not DB_AVAILABLE:
        pytest.skip("MongoDB connection is not available in this environment. Test skipped.")
    return db_manager

@pytest.fixture
def client(test_db_lifecycle):
    """
    Returns a FastAPI TestClient configured with test lifespan events active.
    """
    from app.main import app
    import contextlib

    # If database is not available, bypass app startup events to allow health endpoints tests
    if not DB_AVAILABLE:
        @contextlib.asynccontextmanager
        async def dummy_lifespan(app):
            yield
        app.router.lifespan_context = dummy_lifespan

    with TestClient(app) as test_client:
        yield test_client
