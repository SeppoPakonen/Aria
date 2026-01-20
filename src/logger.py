import logging
import os
import json
import datetime
import time
import functools
import uuid
import contextvars

# Context variable to store the trace ID for the current execution context
trace_id_var = contextvars.ContextVar("trace_id", default=None)

# Context variable to store secrets that should be redacted from logs
secrets_var = contextvars.ContextVar("secrets", default=set())

# Global list to store performance metrics for the current execution
_performance_metrics = []

def add_secret(secret):
    """Adds a secret to the current context for redaction in logs."""
    if not secret or not isinstance(secret, str):
        return
    secrets = secrets_var.get().copy()
    secrets.add(secret)
    secrets_var.set(secrets)

def redact(text):
    """Redacts registered secrets from the given text."""
    if not isinstance(text, str):
        return text
    secrets = secrets_var.get()
    if not secrets:
        return text
    
    # Sort secrets by length descending to avoid partial redaction
    # if one secret is a substring of another.
    for secret in sorted(secrets, key=len, reverse=True):
        if secret and len(secret) > 3: # Avoid redacting very short strings
            text = text.replace(secret, "[REDACTED]")
    return text

class RedactingFilter(logging.Filter):
    """Filter that redacts secrets from log records."""
    def filter(self, record):
        if isinstance(record.msg, str):
            record.msg = redact(record.msg)
        
        if record.args:
            if isinstance(record.args, tuple):
                record.args = tuple(redact(arg) if isinstance(arg, str) else arg for arg in record.args)
            elif isinstance(record.args, dict):
                record.args = {k: redact(v) if isinstance(v, str) else v for k, v in record.args.items()}
        
        # Also redact extra attributes
        for key, value in record.__dict__.items():
            if key not in {'msg', 'args'} and isinstance(value, str):
                # We skip standard attributes that shouldn't be redacted or don't contain secrets
                if not key.startswith('_') and key not in {'levelname', 'name', 'pathname', 'filename', 'module', 'funcName'}:
                    setattr(record, key, redact(value))
        
        return True

class RedactingFormatter(logging.Formatter):
    """Formatter that redacts secrets from the log message (backup if filter is not used)."""
    def format(self, record):
        formatted = super().format(record)
        return redact(formatted)

class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "name": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
        }
        
        # Add trace_id from context if available
        trace_id = trace_id_var.get()
        if trace_id:
            log_record["trace_id"] = trace_id

        if hasattr(record, "extra_context"):
            log_record.update(record.extra_context)
        
        # Add standard record attributes that might be useful
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        
        # Include any extra attributes passed via the 'extra' parameter in logging calls
        # We filter out standard record attributes
        standard_attrs = {
            'args', 'asctime', 'created', 'exc_info', 'filename', 'funcName', 'levelname',
            'levelno', 'lineno', 'module', 'msecs', 'message', 'msg', 'name', 'pathname',
            'process', 'processName', 'relativeCreated', 'stack_info', 'thread', 'threadName'
        }
        for key, value in record.__dict__.items():
            if key not in standard_attrs and not key.startswith('_'):
                log_record[key] = value

        return json.dumps(log_record)

def time_it(logger=None):
    """Decorator to measure and log execution time of a function."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                duration_ms = (end_time - start_time) * 1000
                duration_ms = round(duration_ms, 2)
                
                # Store metric
                _performance_metrics.append({
                    "operation": func.__name__,
                    "duration_ms": duration_ms,
                    "timestamp": datetime.datetime.now().isoformat()
                })
                
                log = logger or logging.getLogger(func.__module__)
                log.info(
                    f"Performance: {func.__name__} took {duration_ms:.2f}ms",
                    extra={"duration_ms": duration_ms, "operation": func.__name__}
                )
        return wrapper
    return decorator

def get_performance_metrics():
    """Returns the collected performance metrics."""
    return list(_performance_metrics)

def clear_performance_metrics():
    """Clears the collected performance metrics."""
    global _performance_metrics
    _performance_metrics = []

def setup_logging(level=logging.INFO, json_format=False):
    """Sets up the logging configuration for Aria."""
    aria_dir = os.path.join(os.path.expanduser("~"), ".aria")
    if not os.path.exists(aria_dir):
        os.makedirs(aria_dir)
    
    log_file = os.path.join(aria_dir, "aria.log")
    
    # Define formatters
    if json_format:
        file_formatter = JsonFormatter()
    else:
        file_formatter = RedactingFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    console_formatter = RedactingFormatter('%(levelname)s: %(message)s')
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addFilter(RedactingFilter())
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # Silence third-party loggers
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("selenium").setLevel(logging.ERROR)
    logging.getLogger("webdriver_manager").setLevel(logging.ERROR)

def get_logger(name):
    """Returns a logger instance for the given name."""
    return logging.getLogger(name)

def set_trace_id(trace_id=None):
    """Sets the trace ID for the current context. Generates one if not provided."""
    if trace_id is None:
        trace_id = str(uuid.uuid4())
    trace_id_var.set(trace_id)
    return trace_id

def get_trace_id():
    """Returns the trace ID for the current context."""
    return trace_id_var.get()
