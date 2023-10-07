import logging

from .handlers import CustomTimedRotatingFileHandler
from .formatters import ColoredStreamFormatter


def setup_logging(logs_dir: str='logs/', set_stream_handler: bool=True):
    """
    Setup logging handlers
    :param logs_dir: the directory for the log files to be sent
    :param set_stream_handler: whether or not to setup a custom stream handler
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(
        CustomTimedRotatingFileHandler(logs_dir=logs_dir))

    if set_stream_handler:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(ColoredStreamFormatter)

        root_logger.addHandler(stream_handler)
