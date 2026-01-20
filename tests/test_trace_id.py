import logging
import json
import io
import unittest
from logger import setup_logging, get_logger, set_trace_id, get_trace_id, JsonFormatter

class TestTraceId(unittest.TestCase):
    def test_trace_id_integration(self):
        # Reset trace ID for this test
        from logger import trace_id_var
        trace_id_var.set(None)

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
        self.assertEqual(get_trace_id(), "test-trace-123")
        logger.info("Message with trace ID")
        
        # 3. Log with extra context
        logger.info("Message with trace ID and extra", extra={"foo": "bar"})
        
        output = log_stream.getvalue().strip().split('\n')
        
        # Verify first log
        log1 = json.loads(output[0])
        self.assertNotIn("trace_id", log1)
        
        # Verify second log
        log2 = json.loads(output[1])
        self.assertEqual(log2["trace_id"], "test-trace-123")
        
        # Verify third log
        log3 = json.loads(output[2])
        self.assertEqual(log3["trace_id"], "test-trace-123")
        self.assertEqual(log3["foo"], "bar")

if __name__ == "__main__":
    unittest.main()
