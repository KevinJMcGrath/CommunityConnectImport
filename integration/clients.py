import logging

from simple_salesforce import Salesforce

import config

class SFDCClient:
    def __init__(self):
        self.username = config.salesforce['username']
        self.password = config.salesforce['password']
        self.security_token = config.salesforce['security_token']
        self.domain = 'login' if not config.salesforce['is_sandbox'] else 'test'

        self.internal_client = self.load_client()

    def load_client(self):
        s = Salesforce(username=self.username, password=self.password, security_token=self.security_token,
                       domain=self.domain, client_id='ComCon Onboarding')

        if s.session_id:
            logging.info('Salesforce connection established.')
        else:
            logging.error('Salesforce connection could not be re-established.')
            raise Exception

        return s

    def reconnect_sfdc(self):
        logging.info('Reconnecting to Salesfoce...')
        self.internal_client = self.load_client()