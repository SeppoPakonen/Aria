import logging
import os

def setup_logging(level=logging.INFO):
    """Sets up the logging configuration for Aria."""
    aria_dir = os.path.join(os.path.expanduser("~"), ".aria")
    if not os.path.exists(aria_dir):
        os.makedirs(aria_dir)
    
    log_file = os.path.join(aria_dir, "aria.log")
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            # We don't necessarily want all logs on console by default 
            # to keep CLI output clean, but maybe WARNING and above?
            logging.StreamHandler()
        ]
    )
    
    # Set console handler level to WARNING to avoid cluttering the CLI
    for handler in logging.root.handlers:
        if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
            handler.setLevel(logging.WARNING)
    
    # Silence third-party loggers
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("selenium").setLevel(logging.ERROR)
    logging.getLogger("webdriver_manager").setLevel(logging.ERROR)

def get_logger(name):
    """Returns a logger instance for the given name."""
    return logging.getLogger(name)
