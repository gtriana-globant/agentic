# Structured logs settings with JSON
import logging
import json
import sys
from core.config import settings

class JSONFormatter(logging.Formatter):
    """
    Formats log records as JSON for enterprise log aggregators (e.g., Azure Monitor).
    """
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger_name": record.name,
            "module": record.module,
        }
        
        # Capture stack traces if an exception occurs
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger instance.
    Usage: logger = get_logger(__name__)
    """
    logger = logging.getLogger(name)
    
    # Prevent duplicate handlers if called multiple times
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        
    logger.setLevel(settings.log_level)
    logger.propagate = False
    
    return logger