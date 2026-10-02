import json
import logging
from io import StringIO
from app.utils.logger import JSONFormatter

def test_logger_json_output_fields():
    """
    Verifies that the JSONFormatter converts log records into valid JSON string formats
    containing standard and extra key elements.
    """
    # Create a stream buffer and stream handler
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JSONFormatter())

    # Create local logger instance for isolated testing
    test_logger = logging.getLogger("test_json_logger")
    test_logger.setLevel(logging.INFO)
    test_logger.addHandler(handler)
    test_logger.propagate = False

    # Log message with extra meta attributes
    test_logger.info("Verification of JSON formatting", extra={"user_id": "test-user-123"})

    # Extract log string
    log_output = stream.getvalue().strip()
    assert log_output.startswith("{")
    assert log_output.endswith("}")

    # Parse and validate schema attributes
    parsed = json.loads(log_output)
    assert "timestamp" in parsed
    assert "level" in parsed
    assert "message" in parsed
    assert "logger" in parsed
    assert "module" in parsed
    assert "function" in parsed
    assert "line" in parsed
    assert "extra" in parsed

    # Validate logged contents
    assert parsed["message"] == "Verification of JSON formatting"
    assert parsed["level"] == "INFO"
    assert parsed["logger"] == "test_json_logger"
    assert parsed["extra"]["user_id"] == "test-user-123"
