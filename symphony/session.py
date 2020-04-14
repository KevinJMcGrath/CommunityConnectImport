import logging

from datetime import datetime
from requests import Session as r_session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .authenticate import auth_chooser


class Session:
    def __init__(self, symphony_config: dict):
        self.config = symphony_config

        self.bot_username = self.config['bot_username']
        self.session_token = ''
        self.km_token = ''
        self.session_expiration = None

        self.http_session = r_session()

        self.mount_session()

    def mount_session(self):
        retries = Retry(total=20, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        self.http_session.mount('https://', HTTPAdapter(max_retries=retries))

    def is_authenticated(self):
        return self.session_token and self.session_expiration > datetime.now()

    def authenticate(self):
        if not self.is_authenticated():
            self.session_token, self.km_token, self.session_expiration = auth_chooser(self.config)
            logging.info('Bot client successfully authenticated.')

    def get_rest_headers(self, content_type: str = "application/json", user_agent: str = None):
        return {
            "sessionToken": self.session_token,
            "keyManagerToken": self.km_token,
            "Content-Type": content_type,
            "User-Agent": user_agent if user_agent else "BizOps SDK (Kevin McGrath - BizOps - kevin.mcgrath@symphony.com)"
        }