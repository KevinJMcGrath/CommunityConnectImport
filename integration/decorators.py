import logging

from simple_salesforce import SalesforceExpiredSession, SalesforceMalformedRequest

import integration


def sfdc_connection_check(func):
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SalesforceExpiredSession as sex:
            logging.warning('SFDC Session expired. Attempting to re-establish connection.')
            integration.sfdc_client.reconnect_sfdc()
            return func(*args, **kwargs)
        except SalesforceMalformedRequest as ex:
            status_code = ex.status
            resource_name = ex.resource_name
            content_msg = ex.content[0].get('message', 'Unknown')
            sfdc_error_code = ex.content[0].get('errorCode', '-1')
            field_list = ex.content[0].get('fields', [])

            logging.error(
                f'SFDC Error - Status Code: {status_code} - SFDC Code: {sfdc_error_code} - Resource: {resource_name}')
            logging.error(f'Fields impacted: {",".join(field_list)}')
            logging.error(f'Message: {content_msg}')

            return False
        except Exception as ex:
            logging.error('Generic Exception')
            logging.exception(ex)
            return False
    return wrapper_func