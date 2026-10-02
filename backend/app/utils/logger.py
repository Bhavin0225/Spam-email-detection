import json
import logging
import sys
from datetime import datetime, timezone
from app.config import settings

class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs log records as structured JSON strings.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Identify custom extra arguments passed to the logger
        RESERVED_ATTRS = {
            "args", "asctime", "created", "exc_info", "exc_text", "filename",
            "funcName", "levelname", "levelno", "lineno", "module", "msecs",
            "message", "msg", "name", "pathname", "process", "processName",
            "relativeCreated", "stack_info", "thread", "threadName"
        }
        extra_data = {
            k: v for k, v in record.__dict__.items() if k not in RESERVED_ATTRS
        }
        if extra_data:
            log_data["extra"] = extra_data

        # Include traceback details if an exception is handled
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)

def setup_logger(name: str = "app") -> logging.Logger:
    """
    Sets up a logger instance with JSON formatting and registers stdout handler.
    """
    app_logger = logging.getLogger(name)
    
    # Parse log level
    level_name = settings.LOG_LEVEL.upper()
    level = getattr(logging, level_name, logging.INFO)
    app_logger.setLevel(level)

    # Avoid duplicate handlers
    if not app_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        app_logger.addHandler(handler)

    # Prevent logs from bubbing up to root logger
    app_logger.propagate = False
    
    return app_logger

# Pre-configured global logger
logger = setup_logger()
