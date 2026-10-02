from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import health
from app.database.connection import db_manager
from app.database.collections import init_collections_and_indexes
from app.utils.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle events manager. Executes database connections and index building on startup
    and clean connection pools tear-downs on shutdown.
    """
    logger.info("FastAPI backend application starting up...")
    try:
        # Connect to MongoDB Atlas
        db_manager.connect()
        # Initialize and build required collections and indexes
        init_collections_and_indexes()
        logger.info("Startup sequence completed successfully.")
    except Exception as e:
        logger.critical(f"Startup sequence aborted: Database connection or initialization failed: {str(e)}")
        # Raise to prevent app starting in an unhealthy/unconfigured state
        raise e
        
    yield
    
    logger.info("FastAPI backend application shutting down...")
    # Terminate database connections gracefully
    db_manager.close()
    logger.info("Shutdown sequence completed.")

from app.api import health, auth, admin, predict, feedback, analytics, history, inbox
from app.middleware.rate_limiter import limiter, rate_limit_exceeded_handler
from app.middleware.audit_logger import AuditLoggerMiddleware
from slowapi.errors import RateLimitExceeded

app = FastAPI(
    title="Spam Email Detection System API",
    description="Backend API for suspicious email classification, predictions, and model auditing.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure slowapi limiter state and handlers
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Configure Middlewares (Order of execution: AuditLoggerMiddleware runs inside CORSMiddleware)
app.add_middleware(AuditLoggerMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(predict.router)
app.include_router(feedback.router)
app.include_router(analytics.router)
app.include_router(history.router)
app.include_router(inbox.router)

@app.get("/", tags=["Root"])
def read_root():
    """
    Root entry welcoming client and pointing to documentation.
    """
    return {
        "message": "Welcome to the Spam Email Detection API.",
        "documentation": "/docs"
    }
