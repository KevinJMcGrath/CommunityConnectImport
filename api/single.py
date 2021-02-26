import logging

import config
import api.exceptions as api_ex

from api import onboard
from models.user import SingleUser
from symphony.bot_client import BotClient
from symphony.ib_gen import InfoBarrierManager

"""
    Error Codes for Sypport:
    772-13 - Onboarding Service failed to connect to the ComCon Pod
    153-22 - Inbound Payload was invalid
    830-18 - Sponsor Id did not match an account in Salesforce
"""
def check_sponsor_name(user: SingleUser):
    if onboard.sfdc_account_get_name(user.sponsor_sfdc_id):
        return True


def add_comcon_user(user: SingleUser):
    """
    Adds a user to the Community Connect pod. This method only calls out to Symphony for user creation.
    All other functions are done in the aysnc user_finalize() method
    :param user: SingleUser - data class containing the payload data from the API
    :return: bool, message - returns True, symphony_id if successful, otherwise False and a relevant message for the client
    """
    try:
        sym_client = BotClient(config.bot_config)

        sym_id = onboard.sym_user_id_get(symphony_client=sym_client, email_address=user.email)

        if not sym_id:
            sym_id = onboard.sym_user_create(symphony_client=sym_client, firstname=user.first_name, lastname=user.last_name,
                                    email_address=user.email, company_name=user.company, title=user.title,
                                    department=user.department)

        return sym_id, None
    except api_ex.SymphonyException as ex:
        logging.exception(ex)

        return None, str(ex)
    except Exception as ex:
        logging.exception(ex)

        err_msg = 'Problem communicating with the Symphony Community Service. ' \
                  'Contact support@symphony.com for assistance. CODE: 772-13'
        return None, err_msg


def finalize_user(user: SingleUser, symphony_id: str):
    # Salesforce record Creation
    sponsor_name = onboard.sfdc_account_get_name(user.sponsor_sfdc_id)

    account_id = onboard.sfdc_account_get_id(user.company)
    if not account_id:
        account_id = onboard.sfdc_account_create(user.company)

    if account_id:
        onboard.sfdc_acount_update_sponsor(sponsor_account_id=user.sponsor_sfdc_id, user_account_id=account_id)

        contact_id = onboard.sfdc_contact_get_id(user.email)
        if not contact_id:
            contact_id = onboard.sfdc_contact_create(account_id=account_id, firstname=user.first_name, lastname=user.last_name,
                                        email_address=user.email)

        if contact_id:
            onboard.sfdc_contact_update_sym_id(contact_id=contact_id, sym_user_id=symphony_id)

            onboard.sfdc_email_contact(email_address=user.email, contact_id=contact_id)

    # Symphony record creation
    try:
        sym_client = BotClient(config.bot_config)
        ibm = InfoBarrierManager(sym_client)

        ib_group_id = onboard.sym_ib_group_get(ib_client=ibm, company_name=user.company)

        if not ib_group_id:
            ib_group_id = onboard.sym_ib_group_create(ib_client=ibm, company_name=user.company)
            onboard.sym_ib_group_add_policies(ib_client=ibm, ib_group_id=ib_group_id)

        onboard.sym_ib_group_add_user(ib_client=ibm, ib_group_id=ib_group_id, sym_user_id=symphony_id)
    except Exception as ex:
        logging.exception(ex)


    # Zendesk record creation
    domain_name = user.email.split('@')[1]
    zen_org_id = onboard.zen_company_add(company_name=user.company, email_domain=domain_name,
                                         sponsor_company_name=sponsor_name)

    if zen_org_id:
        onboard.zen_user_add(zendesk_org_id=zen_org_id, firstname=user.first_name, lastname=user.last_name,
                             email_address=user.email)

    onboard.sg_send_internal_notification(user.first_name, user.last_name, user.email, user.company, sponsor_name)

def import_single_user(payload):
    try:
        user = SingleUser(payload)
        domain = user.email.split('@')[1].lower()

        try:
            sym_client = BotClient(config.bot_config)
            ibm = InfoBarrierManager(sym_client)
        except Exception as ex:
            logging.exception(ex)

            err_msg = 'Problem communicating with the Symphony Community Service. ' \
                      'Contact support@symphony.com for assistance. CODE: 772_13'
            return False, err_msg


        # # 0. Check to make
        # sponsor_company_name = salesforce.get_account_name_by_id(user.sponsor_sfdc_id)
        # if not sponsor_company_name:
        #     return False, 'Invalid sponsor account'
        #
        # # 1. Check for existing Account in SFDC
        # # 2. Create/Update SFDC Account
        # logging.info(f'Get/Create SFDC Cccount for {user.company}')
        # account_id = salesforce.get_company_id(user.company)
        #
        # logging.info(f'Updating Account Sponsor. Account Id: {account_id} Sponsor Id: {user.sponsor_sfdc_id}')
        # salesforce.update_company_sponsor(company_id=account_id, sponsor_id=user.sponsor_sfdc_id)
        #
        # # 3. Check for existing Contact in SFDC
        # logging.info(f'Get SFDC Contact for {user.email}')
        # contact_id = salesforce.contact_query(user.email)
        #
        # # 4. Create/Update SFDC Contact
        # if not contact_id:
        #     logging.info(f'Contact does not exist. Creating Contact.')
        #     contact_id = salesforce.insert_contact(account_id=account_id, firstname=user.first_name,
        #                                            lastname=user.last_name, email=user.email)
        #
        #
        # # 5. Check for existing user in Symphony
        # logging.info(f'Get Symphony user Id for {user.email}')
        # sym_user_id = sym_client.User.lookup_user_id(user.email)
        #
        # # 6. Add user to Symphony
        # if not sym_user_id:
        #     logging.info(f'Symphony user does not exist. Creating.')
        #     sym_user_id = sym_client.User.create_symphony_user(user.first_name, user.last_name, user.email,
        #                                          user.email, user.company, title=user.title,
        #                                          department=user.department)
        #
        # logging.info(f'Updating Contact {contact_id} with Community Connect id {sym_user_id}')
        # salesforce.update_contact_symphony_id(contact_id, sym_user_id)
        #
        # # 7. Add IB Group for company
        # cname = user.company.strip().replace(' ', '_')
        # group_name = f"cc_{cname}"
        #
        # is_existing_ib_group = True
        # logging.info(f'Getting Info Barrior group id for {group_name}')
        # ib_group_id = ibm.get_existing_ib_group(group_name)
        #
        # if not ib_group_id:
        #     logging.info(f'IB Group does not exist. Creating.')
        #     ib_group_id = ibm.create_ib_group(group_name)
        #     is_existing_ib_group = False
        #
        # # 8. Add User to IB Group
        # logging.info(f'Adding user to IB Group')
        # ibm.add_users_to_ib_group(group_id=ib_group_id, user_ids=[sym_user_id])
        #
        # # 9. Add IB policy combinations
        # if is_existing_ib_group:
        #     logging.info('IB Group previously existed. Skipping policy creation')
        # else:
        #     logging.info('Creating IB Group policy combinations')
        #     ibm.create_all_policy_combinations(ib_group_id)
        #
        # # 10. Create/Update user in Zendesk
        # logging.info(f'Get/Create Zendesk Org')
        # zen_company = zen.get_or_add_org(user.company, domain=domain, sponsor_name=sponsor_company_name)
        # zen_company_id = zen_company.id
        #
        # # 11. Create/Update user in Zendesk
        # logging.info(f'Get/Create Zendesk User')
        # zen_user = zen.get_or_add_user(fullname=f'{user.first_name} {user.last_name}', email=user.email,
        #                                   org_id=zen_company_id)
        #
        # # 13. Email user
        # logging.info('Sending user welcome email')
        # salesforce.send_single_welcome_email(email=user.email, contact_id=contact_id)
        #
        # # 14. Email onboarding/support
        # # sg.send_email(from_address='kevin.mcgrath@symphony.com', to_addresses=[''])

        return True, None
    except Exception as ex:
        logging.exception(ex)
        return False, str(ex)


