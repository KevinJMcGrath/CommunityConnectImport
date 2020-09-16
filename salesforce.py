import logging

from typing import List, Dict

from simple_salesforce import Salesforce

import config

from models.user import ImportedUser

if config.salesforce['is_sandbox']:
    sfdc = Salesforce(username=config.salesforce['username'], password=config.salesforce['password'],
                      security_token=config.salesforce['security_token'], domain='test')
else:
    sfdc = Salesforce(username=config.salesforce['username'], password=config.salesforce['password'],
                          security_token=config.salesforce['security_token'])
log = logging.getLogger()


def import_salesforce_single_user(user: ImportedUser):
    company_id = get_company_id(user.company)

    if company_id:
        update_company_sponsor(company_id, user.sponsor_sfdc_id)
    else:
        return False, 'Unable to save Account to Salesforce'

    if not get_user(user, company_id):
        return False, 'Unable to save Contact to Salesforce'



def import_salesforce_users(user_dict: dict):
    return_dict = {}
    for company_name, user_list in user_dict.items():
        company_id = get_company_id(company_name)
        sponsor_id = user_list[0].sponsor_sfdc_id

        if company_id:
            update_company_sponsor(company_id, sponsor_id)

            return_list = []
            for user in user_list:
                if get_user(user, company_id):
                    return_list.append(user)

            return_dict[company_name] = return_list



def get_user(user_record: ImportedUser, company_id: str):
    user_id, acct_id = search_user(user_record.email)

    if user_id:
        log.info(f'{user_record.email} exists in SFDC with Id: {user_id}')
        user_record.sfdc_account_id = acct_id
        user_record.sfdc_id = user_id
        return True
    else:
        log.info(f'Creating Contact for email address: {user_record.email}')
        return insert_user(user_record, company_id)



def insert_user(user_record: ImportedUser, company_id: str):
    user_payload = {
        "AccountId": company_id,
        "FirstName": user_record.first_name,
        "LastName": user_record.last_name,
        "Email": user_record.email
    }

    result = sfdc.Contact.create(user_payload)

    if result['success']:
        user_record.sfdc_id = result['id']
        user_record.sfdc_account_id = company_id

        add_contact_roles(user_record)

        return True
    else:
        log.error('Error creating Contact')
        for err in result['errors']:
            log.error(err)

        return None


def update_contact_symphony_ids(user_dict: Dict[str, List[ImportedUser]]):
    log.info('Updating Contacts with Community Connect Ids')
    payload_list = []

    for user_list in user_dict.values():
        for user in user_list:
            payload_list.append({
                "Id": user.sfdc_id,
                "Community_Pod_Id__c": user.symphony_id
            })

    sfdc.bulk.Contact.update(payload_list)

def add_contact_roles(user_record: ImportedUser):
    pass


def search_user(email_address: str):
    soql = f"SELECT Id, AccountId FROM Contact WHERE Email ='{email_address}'"

    results = sfdc.query(soql)['records']

    if results:
        record = results[0]
        return record['Id'], record['AccountId']

    return None, None

def search_users_no_import(company_user_dict):
    for _, company_users in company_user_dict.items():
        for user in company_users:
            sfdc_id, account_id = search_user(user.email)

            if sfdc_id:
                user.sfdc_id = sfdc_id


def get_company_id(company_name: str):
    # company_id = company_search(company_name)
    company_id = company_query(company_name)

    if not company_id:
        log.info(f'{company_name} does not exist. Creating Account in Salesforce.')
        company_id = insert_company(company_name)


    return company_id


def company_query(company_name: str):
    soql = f"SELECT Id FROM Account WHERE Name = '{company_name}'"

    results = sfdc.query(soql)['records']

    if results:
        record = results[0]
        return record['Id']

    return None


def company_search(company_name: str):
    # sosl_query = 'FIND {' + company_name + '} IN NAME FIELDS RETURNING Account(Id, Name)'
    results = sfdc.quick_search(company_name)['searchRecords']

    for res in results:
        if res['attributes']['type'] == 'Account':
            sfdc_id = res['Id']
            log.info(f'{company_name} found in Salesforce - Id: {sfdc_id}')
            return sfdc_id

    return None


def insert_company(company_name: str):
    company_payload = {
        'Name': company_name,
        'Type': 'Community Connect',
        'Industry': 'Financial Services',
        'Industry_Sub_Type__c': 'Private Equity',
        'Financial_Services_Category__c': 'Buy Side'
    }

    result = sfdc.Account.create(company_payload)

    if result['success']:
        return result['id']
    else:
        log.error('Error creating account')
        for err in result['errors']:
            log.error(err)

        return None

def update_company_sponsor(company_id: str, sponsor_id: str):
    company_payload = {
        'Symphony_CP_Sponsor__c': sponsor_id
    }

    result = sfdc.Account.update(company_id, company_payload)

    if result != 204:
        log.error('Error updating Account sponor reference')

def send_email_test():
    user = {
        "to": "kevinmcgr@gmail.com",
        "cc": "templephysicist@gmail.com",
        "bcc": "kevin.mcgrath@symphony.com",
        "template_id": "00X1J0000013Q7p",
        "contact_id": "0031J00001HBHqL",
        "org_email_id": "0D21J0000000Iu4"
    }

    users = [user]

    payload = {
        "users": users
    }

    rest_path = 'symphony/email/template'

    sfdc.apexecute(action=rest_path, method='POST', data=payload)

def send_welcome_email(company_user_dict: dict):
    users_for_email = []

    for _, company_users in company_user_dict.items():
        for u in company_users:
            user = {
                "to": u.email,
                "cc": "",
                "bcc": "sarah@symphony.com",
                "template_id": "00X1J0000013Q7p",
                "contact_id": u.sfdc_id,
                "org_email_id": "0D21J0000000Iu4"
            }

            users_for_email.append(user)

    batch_count, remainder = divmod(len(users_for_email), 10)

    # https://developer.salesforce.com/forums/?id=906F00000008yrGIAQ
    # Because Apex only allows 10 SendEmail invocations per transaction, I need
    # to break this up into chunks to submit.
    # TODO: Change the REST endpoint to a batch system instead.
    if remainder > 0:
        batch_count += 1

    for index in range(batch_count):
        start = index * 10
        end = (index + 1) * 10
        payload = {
            "users": users_for_email[start:end]
        }

        rest_path = 'symphony/email/template'

        resp = sfdc.apexecute(action=rest_path, method='POST', data=payload)



def send_bizops_notification():
    pass

def send_account_owner_notification():
    pass