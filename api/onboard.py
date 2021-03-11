import logging

from datetime import datetime

import api.exceptions as api_ex

from integration import salesforce
from integration import sendgrid as sg
from integration import zendesk as zen
from symphony.bot_client import BotClient
from symphony.ib_gen import InfoBarrierManager


sfdc_err_log = logging.getLogger('SFDC_API_ERROR')
sym_err_log = logging.getLogger('SYM_API_ERROR')
zen_err_log = logging.getLogger('ZEN_API_ERROR')
sg_err_log = logging.getLogger('SG_API_ERROR')

def sfdc_promo_code_lookup_account_id(sponsor_code: str):
    """
    Looks up the Account Id based on the provided promo code
    :param sponsor_code:
    :return: SFDC Account Id
    """
    account_id = ''
    err_msg = ''

    logging.info(f'Looking up SFDC Account Id for sponsor code {sponsor_code}')
    promo_code = salesforce.get_promo_by_sponspor_code(sponsor_code)

    if not promo_code:
        err_msg = f'Sponsor Code could not be matched to an account.'
    elif promo_code['Disabled__c']:
        err_msg = f'Sponsor Code has been disabled. Please contact support for assistance.'
    elif promo_code['Expired__c']:
        err_msg = f'Sponsor Code has expired. Please contact support for assistance.'
    elif promo_code['Redeemed__c']:
        err_msg = f'Sponsor Code has been fully redeemed and is no longer valid. Please contact support for assistance.'
    # else:
    #     account_id = promo_code['Community_Connect_Sponsor__c']

    if err_msg:
        sfdc_err_log.error(err_msg)

    return promo_code, err_msg


def sfdc_increment_promo_code_redemptions(promo_code):
    promo_code_id = promo_code['Id']
    redemptions = promo_code['Redemptions__c'] + 1 if promo_code['Redemptions__c'] else 1

    salesforce.update_promo_code_redemptions(promo_code_id, redemptions)


# 0. Check to make
def sfdc_account_get_name(sfdc_id: str):
    """
    :param sfdc_id:
    :return: Sponsor Account Name (str) if exists, otherwise returns None
    """
    logging.info(f'Getting Account name for id {sfdc_id}')
    sponsor_company_name = salesforce.get_account_name_by_id(sfdc_id)

    if not sponsor_company_name:
        sfdc_err_log.error(f'Account Id {sfdc_id} could not be located in Salesforce')

    return sponsor_company_name


# 1a. Check for existing Account in SFDC
def sfdc_account_get_id(company_name):
    """
        :param company_name:
        :return: SFDC Acconunt Id (str) if Account exists in Salesforce, otherwise returns None
        """
    logging.info(f'Checking if {company_name} exists in Salesforce')
    account_id = salesforce.company_query(company_name)

    if not account_id:
        logging.debug(f'Company {company_name} does not exist in Salesforce')

    return account_id


# 1b. Create SFDC Account
def sfdc_account_create(company_name):
    """
    :param company_name:
    :return: SFDC Acconunt Id (str) if successful, otherwise returns None
    """
    logging.info(f'Creating SFDC Cccount for {company_name}')
    account_id = salesforce.insert_company(company_name)

    if not account_id:
        sfdc_err_log.error(f'Failed to create Salesforce Account for {company_name}')

    return account_id


# 2. Update Sponsor Account
def sfdc_acount_update_sponsor(sponsor_account_id: str, user_account_id: str):
    """
    :param sponsor_account_id:
    :param user_account_id:
    :return: 204 if update succeeds, otherwise returns False
    """
    logging.info(f'Updating Account Sponsor. Account Id: {user_account_id} Sponsor Id: {sponsor_account_id}')

    if sponsor_account_id[:15] == user_account_id[:15]:
        err_msg = f'Sponsor Account Id ({sponsor_account_id}) and User Account Id ({user_account_id}) ' \
                  f'reference the same account.'

        sfdc_err_log.error(err_msg)
        return False

    return salesforce.update_company_sponsor(company_id=user_account_id, sponsor_id=sponsor_account_id)


# 3. Check for existing Contact in SFDC
def sfdc_contact_get_id(email_address: str):
    logging.info(f'Get SFDC Contact for {email_address}')
    contact_id = salesforce.contact_query(email_address)

    if not contact_id:
        logging.debug(f'Contact does not exist for email {email_address}')

    return contact_id


# 4. Create SFDC Contact
def sfdc_contact_create(account_id: str, firstname: str, lastname: str, email_address: str):
    """    
    :param account_id: 
    :param firstname: 
    :param lastname: 
    :param email_address: 
    :return: SFDC Contact Id if successful otherwise returns False 
    """
    logging.info(f'Creating SFDC Contact for email: {email_address} under Account Id: {account_id}')

    contact_id = salesforce.insert_contact(account_id=account_id, firstname=firstname, lastname=lastname,
                                           email=email_address)

    if not contact_id:
        sfdc_err_log.error(f'Unable to create Contact for email {email_address}')
        
    return contact_id


# 7. Update SFDC Contact with Symphony Id
def sfdc_contact_update_sym_id(contact_id: str, sym_user_id):
    logging.info(f'Updating Contact {contact_id} with Community Connect id {sym_user_id}')
    salesforce.update_contact_symphony_id(contact_id, sym_user_id)


# 13. Email user
def sfdc_email_contact(email_address: str, contact_id: str):
    logging.info('Sending user welcome email')
    salesforce.send_single_welcome_email(email=email_address, contact_id=contact_id)
    

# 5. Check for existing user in Symphony
def sym_user_id_get(symphony_client: BotClient, email_address: str):
    logging.info(f'Get Symphony user Id for {email_address}')
    
    try:
        return symphony_client.User.lookup_user_id(email_address)
    except Exception as ex:
        sym_err_log.exception(ex)
        
        raise api_ex.SymphonyException(f'There was a problem creating your user account. Please contact support. CODE: 011-54')

# 6. Add user to Symphony
def sym_user_create(symphony_client: BotClient, firstname: str, lastname: str, email_address: str, company_name: str,
                    title: str='', department: str=''):

    logging.info(f'Creating Symphony user for email {email_address} under company name {company_name}')

    try:
        return symphony_client.User.create_symphony_user(first_name=firstname, last_name=lastname, email=email_address,
                                                         username=email_address, company_name=company_name, title=title,
                                                         department=department)
    except Exception as ex:
        sym_err_log.exception(ex)

        raise api_ex.SymphonyException(f'User creation for {email_address} failed with exception')


# 8. Add IB Group for company
def sym_ib_group_get(ib_client: InfoBarrierManager, company_name: str):
    cname = company_name.strip().replace(' ', '_')
    group_name = f"cc_{cname}"
    logging.info(f'Getting Info Barrior group id for {group_name}')

    return ib_client.get_existing_ib_group(group_name)


# 9. Create IB Group for company
def sym_ib_group_create(ib_client: InfoBarrierManager, company_name: str):
    cname = company_name.strip().replace(' ', '_')
    group_name = f"cc_{cname}"
    logging.info(f'Creating Info Barrior group for {group_name}')

    try:
        return ib_client.create_ib_group(group_name)
    except Exception as ex:
        sym_err_log.exception(ex)


# 9. Add User to IB Group
def sym_ib_group_add_user(ib_client: InfoBarrierManager, ib_group_id: str, sym_user_id):
    logging.info(f'Adding user to IB Group')

    try:
        ib_client.add_users_to_ib_group(group_id=ib_group_id, user_ids=[sym_user_id])
    except Exception as ex:
        sym_err_log.exception(ex)


# 10. Add IB policy combinations
def sym_ib_group_add_policies(ib_client: InfoBarrierManager, ib_group_id: str):
    logging.info(f'Creating IB Group policy combinations for group id {ib_group_id}')
    ib_client.create_all_policy_combinations(ib_group_id)


# 11. Create/Update user in Zendesk
def zen_company_add(company_name: str, email_domain: str, sponsor_company_name: str):
    logging.info(f'Add/Update Zendesk Org for {company_name}')

    try:
        zen_company = zen.get_or_add_org(company_name=company_name, domain=email_domain, sponsor_name=sponsor_company_name)
        return zen_company.id
    except Exception as ex:
        zen_err_log.exception(ex)


# 12. Create/Update user in Zendesk
def zen_user_add(zendesk_org_id: str, firstname: str, lastname: str, email_address: str):
        logging.info(f'Add/Update Zendesk User for {email_address}')

        try:
            zen_user = zen.get_or_add_user(fullname=f'{firstname} {lastname}', email=email_address,
                                           org_id=zendesk_org_id)
        except Exception as ex:
            zen_err_log.exception(ex)


# 14. Email onboarding/support
def sg_send_internal_notification(first_name: str, last_name: str, email: str, company_name: str, sponsor_name: str):
    subj = f'ComCon User Onboarded: {first_name} {last_name} - {company_name}'
    body = f"""
        <html><body>
            <p style="font-size:1.2em;">New Community Connect User has been onboarded via self-service.</p>
            <ul style="margin:20px;">
                <li><b>Sponsor Name</b>: {sponsor_name}</li>
                <li><b>Company Name</b>: {company_name}</li>
                <li><b>Name</b>: {first_name} {last_name}</li>
                <li><b>Email</b>: {email}</li>
            </ul>
            <p>User has been sent the Welcome notification and all Salesforce and Zendesk records have been created.</p>
        </body></html>
    """

    to_adds = ['kevin.mcgrath@symphony.com', 'miguel.clark@symphony.com', 'sharon.hackett@symphony.com']
    sg.send_email_async(from_address='onboarding@symphony.com', to_addresses=to_adds, subject=subj, body_html=body)


def sg_send_internal_failure_notification_bulk(failed_users: dict):
    if not failed_users:
        return

    failed_headers = ['Email', 'Error']
    failed_data = []

    for user, err in failed_users.items():
        failed_data.append([user.email, err])

    fn_date = datetime.now().isoformat().replace(':', '_')
    filename = f'comcon_failed_users_{fn_date}.csv'

    att = sg.create_attachment_csv(filename=filename, headers=failed_headers, data=failed_data)

    from_email = 'onboarding@symphony.com'
    to_addy = ['kevinmcgr@gmail.com']
    subj = 'ComCon Users what failed to onboard'
    body = f"""
    <html>
    <body>
        <p style="font-size:1.2em;">Some users could not be onboarded. See attachment</p>
    </body>
    </html>
    """
    sg.send_email(from_address=from_email, to_addresses=to_addy, subject=subj, body_html=body, attachment_list=[att])


def sg_send_internal_success_notification_bulk(success_users: list):
    if not success_users:
        return

    success_data = []
    succes_headers = ['Email', 'Company', 'Sponsor', 'Sponsor_Id']
    for user in success_users:
        u = [user.email, user.company, user.sponsor_account_name, user.sponsor_account_id]


    fn_date = datetime.now().isoformat().replace(':', '_')
    filename = f'comcon_success_users_{fn_date}.csv'

    att = sg.create_attachment_csv(filename=filename, headers=succes_headers, data=success_data)

    from_email = 'onboarding@symphony.com'
    to_addy = ['kevinmcgr@gmail.com']
    subj = 'ComCon Users successfully onboarded'
    body = f"""
    <html>
    <body>
        <p style="font-size:1.2em;">Bulk onboarding complete. See attachment for list of successfully onboarded users.</p>
    </body>
    </html>
    """
    sg.send_email(from_address=from_email, to_addresses=to_addy, subject=subj, body_html=body, attachment_list=[att])