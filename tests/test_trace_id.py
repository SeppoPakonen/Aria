import logging
import json
import io
from src.logger import setup_logging, get_logger, set_trace_id, get_trace_id, JsonFormatter

def test_trace_id_integration():
    # Setup a logger with JsonFormatter writing to a stream
    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setFormatter(JsonFormatter())
    
    logger = logging.getLogger("test_trace")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    # 1. Log without trace ID
    logger.info("Message without trace ID")
    
    # 2. Set trace ID and log
    trace_id = set_trace_id("test-trace-123")
    assert get_trace_id() == "test-trace-123"
    logger.info("Message with trace ID")
    
    # 3. Log with extra context
    logger.info("Message with trace ID and extra", extra={"foo": "bar"})
    
    output = log_stream.getvalue().strip().split('\n')
    
    # Verify first log
    log1 = json.loads(output[0])
    print(f"Log 1: {log1}")
    assert "trace_id" not in log1
    
    # Verify second log
    log2 = json.loads(output[1])
    print(f"Log 2: {log2}")
    assert log2["trace_id"] == "test-trace-123"
    
    # Verify third log
    log3 = json.loads(output[2])
    print(f"Log 3: {log3}")
    assert log3["trace_id"] == "test-trace-123"
    assert log3["foo"] == "bar"
    
    print("Test passed!")

if __name__ == "__main__":
    test_trace_id_integration()
