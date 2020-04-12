import jsonpickle
import logging
import logging.handlers

from pathlib import Path

config_path = Path("./config.json")

with open(config_path, 'r') as _config_file:
    _config = jsonpickle.decode(_config_file.read())

import_path = _config['import_path']
bot_config = _config['bot_config']
salesforce = _config['salesforce']


# config logger

_logger = logging.getLogger()
_logger.setLevel(logging.DEBUG)
_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

