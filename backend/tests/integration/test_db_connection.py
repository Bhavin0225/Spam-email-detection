import pytest
from pymongo.errors import ConnectionFailure
from app.database.connection import db_manager

def test_database_connection_ping(require_db):
    """
    Asserts that connection manager initializes and successfully pings the database server.
    """
    try:
        ping_response = db_manager.ping()
        assert ping_response is not None
        assert "ok" in ping_response
        assert float(ping_response["ok"]) == 1.0
    except ConnectionFailure as e:
        pytest.fail(f"MongoDB ping assertion failed. The database is unreachable: {str(e)}")
