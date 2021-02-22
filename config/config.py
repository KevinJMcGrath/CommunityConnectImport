import jsonpickle
import os

from pathlib import Path

from models.config import LogType

deploy_type = os.environ.get('DEPLOY_TYPE')

if deploy_type == 'prod':
    config_path = '/etc/comcon_import/config/config.json'
else:
    config_path = Path("config/config.json")

with open(config_path, 'r') as _config_file:
    _config = jsonpickle.decode(_config_file.read())

import_path = _config['import_path']
pod_company_name = _config['pod_company_name']
api_key = _config['api_key']
bot_config = _config['bot_config']
salesforce = _config['salesforce']
zendesk = _config['zendesk']
sendgrid = _config['sendgrid']

if deploy_type == 'prod':
    bot_config['secrets_folder'] = '/etc/comcon_import/config'

LogConfig = LogType(_config['logging'])


