import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.config import settings
from app.utils.logger import logger

class DatabaseConnectionManager:
    """
    Manages MongoDB client lifecycle, connection pools, pings, and clean shutdowns.
    """
    def __init__(self):
        self._client = None
        self._db = None

    def connect(self) -> None:
        """
        Initializes PyMongo MongoClient with retry support, pooling settings, and timeout controls.
        """
        if self._client is not None:
            return

        try:
            logger.info("Initializing MongoDB Atlas connection pool...")
            
            # Establish client with connection pool and retry options
            self._client = pymongo.MongoClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=5000,  # fail fast on bad connections (5 seconds)
                connectTimeoutMS=5000,
                retryWrites=True,
                retryReads=True,
                maxPoolSize=50,
                minPoolSize=10
            )
            
            self._db = self._client[settings.MONGODB_DATABASE]
            
            # Verify database connection by sending ping
            self.ping()
            logger.info(f"MongoDB connected successfully. Database: '{settings.MONGODB_DATABASE}'")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.critical(f"Could not connect to MongoDB Atlas at configured URI: {str(e)}")
            self.close()
            raise ConnectionFailure(f"Database connection initialization failed: {str(e)}") from e

    def ping(self) -> dict:
        """
        Executes a cheap ping command on admin database to verify the service is responsive.
        """
        if self._client is None:
            raise ConnectionFailure("MongoDB client has not been initialized.")
        try:
            return self._client.admin.command("ping")
        except Exception as e:
            logger.error(f"Database connection health check (ping) failed: {str(e)}")
            raise ConnectionFailure(f"Ping failed: {str(e)}") from e

    @property
    def db(self) -> pymongo.database.Database:
        """
        Lazy-loads client connection and returns target database instance.
        """
        if self._db is None:
            self.connect()
        return self._db

    @property
    def client(self) -> pymongo.MongoClient:
        """
        Lazy-loads client connection and returns raw client instance.
        """
        if self._client is None:
            self.connect()
        return self._client

    def close(self) -> None:
        """
        Gracefully terminates all socket connections in MongoClient's connection pool.
        """
        if self._client is not None:
            logger.info("Closing MongoDB client connection pool...")
            self._client.close()
            self._client = None
            self._db = None
            logger.info("MongoDB client connections terminated.")

# Singleton manager instance
db_manager = DatabaseConnectionManager()
