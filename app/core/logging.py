import logging
import sys
from logging import Formatter
import json
from app.core.config import settings

class JsonFormatter(Formatter):
    def format(self, record):
        data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.msg,
            "module": record.module,
            "function": record.funcName,
        }
        return json.dumps(data)

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(settings.LOG_LEVEL)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JsonFormatter())
    logger.addHandler(console_handler)
    
    # File handler for persistence
    file_handler = logging.FileHandler("app.log")
    file_handler.setFormatter(JsonFormatter())
    logger.addHandler(file_handler)