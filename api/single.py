import logging

import config
import api.exceptions as api_ex

from api import onboard
from models.user import SingleUser
from symphony.bot_client import BotClient
from symphony.ib_gen import InfoBarrierManager


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
            contact_id = onboard.sfdc_contact_create(account_id=account_id, firstname=user.first_name,
                                                     lastname=user.last_name, email_address=user.email)

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