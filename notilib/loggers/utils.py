import logging

from .handlers import CustomTimedRotatingFileHandler
from .formatters import ColoredStreamFormatter


def setup_logging():
    """Setup logging handlers"""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(CustomTimedRotatingFileHandler())

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(ColoredStreamFormatter)

    root_logger.addHandler(stream_handler)
