from pathlib import Path

import symphony.authenticate.auth_cert as auth_cert
import symphony.authenticate.auth_jwt as auth_jwt


def auth_chooser(symphony_config: dict):
    auth_base_url = symphony_config['auth_host'] + ':' + symphony_config['auth_port']

    if symphony_config['auth_type'] == 'CERT':
        cert_path = Path(f'{symphony_config["secrets_folder"]}/{symphony_config["cert_filename"]}')
        key_path = Path(f'{symphony_config["secrets_folder"]}/{symphony_config["key_filename"]}')
        return authenticate_by_certificate(auth_base_url, cert_path, key_path)
    elif symphony_config['auth_type'] == 'JWT':
        bot_username = symphony_config['bot_username']
        private_key_path = Path(f'{symphony_config["secrets_folder"]}/{symphony_config["private_key_filename"]}')
        return authenticate_by_jwt(auth_base_url, bot_username, private_key_path)


def authenticate_by_certificate(auth_base_url: str, cert_path: str, key_path: str):
    return auth_cert.authenticate_bot(auth_base_url, cert_path, key_path)


def authenticate_by_jwt(auth_base_url: str, bot_username: str, private_key_path: str):
    return auth_jwt.authenticate_bot_by_keyfile(auth_base_url, bot_username, private_key_path)
