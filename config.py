import jsonpickle

from pathlib import Path

from models.config import LogType

config_path = Path("./config.json")

with open(config_path, 'r') as _config_file:
    _config = jsonpickle.decode(_config_file.read())

import_path = _config['import_path']
pod_company_name = _config['pod_company_name']
bot_config = _config['bot_config']
salesforce = _config['salesforce']

LogConfig = LogType(_config['logging'])


