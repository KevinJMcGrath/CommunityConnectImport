import logging.handlers
import sys

from pathlib import Path


# Log Filter class
class LogFilter:
    def __init__(self, level):
        self.__level = level

    def filter(self, log_record):
        return log_record.levelno <= self.__level


# Define the root logging instance
root_logger = logging.getLogger('')
root_logger.setLevel(logging.DEBUG)

# File Paths
debug_log_path = Path('./logs/debug.log')
info_log_path = Path('./logs/info.log')
error_log_path = Path('./logs/error.log')

# Log Formatting
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
formatter.datefmt = '%m/%d %H:%M:%S'


def initialize_logging(verbose_mode: bool=True, log_to_files: bool=True):
    def set_handler_type(log_file_path=Path('./logs/default.log'), max_log_size: int = 50_000, stream=sys.stdout,
                       force_stream: bool = False):

        if force_stream or not log_to_files:
            return logging.StreamHandler(stream)
        else:
            return logging.handlers.TimedRotatingFileHandler(filename=log_file_path,
                                                             when="d", interval=1, backupCount=1)
            # return logging.handlers.RotatingFileHandler(filename=log_file_path, maxBytes=max_log_size, backupCount=7)

    # Define the logging handlers
    if verbose_mode:
        console_handler = set_handler_type(force_stream=True)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter('%(message)s'))
        console_handler.addFilter(LogFilter(logging.INFO))
        root_logger.addHandler(console_handler)

        debug_handler = set_handler_type(log_file_path=debug_log_path, max_log_size=200_000)
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(formatter)
        debug_handler.addFilter(LogFilter(logging.DEBUG))
        root_logger.addHandler(debug_handler)

    info_handler = set_handler_type(log_file_path=info_log_path)
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)
    info_handler.addFilter(LogFilter(logging.WARN))
    root_logger.addHandler(info_handler)

    error_handler = set_handler_type(log_file_path=error_log_path, stream=sys.stderr)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    error_handler.addFilter(LogFilter(logging.ERROR))
    root_logger.addHandler(error_handler)





