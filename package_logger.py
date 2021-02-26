import logging.handlers
import sys

import config

# Log Filter class
class LogFilter(logging.Filter):
    def __init__(self, level):
        super().__init__()

        self.__level = level

    def filter(self, log_record):
        return log_record.levelno <= self.__level


# Define the root logging instance
root_logger = logging.getLogger('')

log_level = logging.DEBUG if config.LogConfig.verbose else logging.INFO
root_logger.setLevel(logging.DEBUG)


# Log Formatting
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
formatter.datefmt = '%m/%d %H:%M:%S'


def initialize_logging():
    # Define the logging handlers
    if config.LogConfig.verbose:
        debug_handler = logging.StreamHandler(stream=sys.stdout)
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(formatter)
        debug_handler.addFilter(LogFilter(logging.DEBUG))
        root_logger.addHandler(debug_handler)

    info_handler = logging.StreamHandler(stream=sys.stdout)
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)
    info_handler.addFilter(LogFilter(logging.WARN))
    root_logger.addHandler(info_handler)

    error_handler = logging.StreamHandler(stream=sys.stderr)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    error_handler.addFilter(LogFilter(logging.ERROR))
    root_logger.addHandler(error_handler)





