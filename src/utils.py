import time
import random
import functools
import logging
from logger import get_logger

logger = get_logger("utils")

def retry(exceptions, tries=3, delay=1, backoff=2, jitter=0.1, logger=logger):
    """
    Retry decorator with exponential backoff and jitter.
    
    Args:
        exceptions: Exception or tuple of exceptions to catch.
        tries: Maximum number of attempts.
        delay: Initial delay between retries in seconds.
        backoff: Multiplier applied to delay after each retry.
        jitter: Random jitter range (as fraction of current delay) to add/subtract.
        logger: Logger instance to use for reporting retries.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            m_tries, m_delay = tries, delay
            while m_tries > 1:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    # Calculate wait time with jitter
                    wait = m_delay * (1 + random.uniform(-jitter, jitter))
                    logger.warning(
                        f"Retrying {func.__name__} in {wait:.2f}s due to {e.__class__.__name__}: {e}. "
                        f"{m_tries - 1} attempts remaining."
                    )
                    time.sleep(wait)
                    m_tries -= 1
                    m_delay *= backoff
            
            # Final attempt
            return func(*args, **kwargs)
        return wrapper
    return decorator
