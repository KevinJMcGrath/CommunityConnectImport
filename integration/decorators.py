import logging

from simple_salesforce import SalesforceExpiredSession

import integration


def sfdc_connection_check(func):
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SalesforceExpiredSession as sex:
            logging.warning('SFDC Session expired. Attempting to re-establish connection.')
            integration.sfdc_client.reconnect_sfdc()
            return func(*args, **kwargs)
    return wrapper_func