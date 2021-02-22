import logging

from simple_salesforce import Salesforce, SalesforceExpiredSession

import config
import package_logger










sfdc_client = SFDCClient()

@sfdc_client.sfdc_reconnect
def query_sfdc(limit: int):
    soql = f"SELECT Id, Name FROM Account LIMIT {limit}"
    accounts = sfdc_client.internal_client.query(soql)['records']

    for a in accounts:
        print(f"Id: {a['Id']} - Name: {a['Name']}")



def run_test():
    package_logger.initialize_logging()
    query_sfdc(2)

    query_sfdc(4)

if __name__ == '__main__':
    run_test()