import logging
import sys


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configures the root logger to output to stdout with a standard format.
    
    Args:
        level (int): The logging level to set (default: logging.INFO).
        
    Returns:
        logging.Logger: The configured root logger.
    """
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Clear existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()
        
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
