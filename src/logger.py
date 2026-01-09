import logging
import os
import json
import datetime

class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "name": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
        }
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
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
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
    console_handler.setLevel(logging.WARNING)
    root_logger.addHandler(console_handler)
    
    # Silence third-party loggers
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("selenium").setLevel(logging.ERROR)
    logging.getLogger("webdriver_manager").setLevel(logging.ERROR)

def get_logger(name):
    """Returns a logger instance for the given name."""
    return logging.getLogger(name)
