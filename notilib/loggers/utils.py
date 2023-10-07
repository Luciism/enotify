import logging

from .handlers import CustomTimedRotatingFileHandler
from .formatters import ColoredStreamFormatter


def setup_logging(logs_dir: str='logs/'):
    """
    Setup logging handlers
    :param logs_dir: the directory for the log files to be sent
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(
        CustomTimedRotatingFileHandler(logs_dir=logs_dir))

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(ColoredStreamFormatter)

    root_logger.addHandler(stream_handler)
