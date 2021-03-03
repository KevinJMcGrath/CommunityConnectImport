import logging

from typing import List

import config
import api.exceptions as api_ex

from api import onboard
from models.user import SingleUser
from symphony.bot_client import BotClient
from symphony.ib_gen import InfoBarrierManager


def bulk_import_users(user_list):
    failed_users = {}

    try:
        sym_client = BotClient(config.bot_config)

        ibm = InfoBarrierManager(sym_client)
    except Exception as ex:
        logging.error('Failed to authenticate with CP2')
        logging.exception(ex)
        return

    success_users, failed = create_symphony_users(user_list, sym_client)

    # Python 3.9 notation for merging dicts
    failed_users = failed_users | failed

    success_users, failed = finalize_users(user_list=success_users, sym_client=sym_client, ibm=ibm)

    failed_users = failed_users | failed

    onboard.sg_send_internal_success_notification_bulk(success_users)
    onboard.sg_send_internal_failure_notification_bulk(failed_users)


def bulk_signup_users(user_list):
    success_users = []
    failed_users = {}


def create_symphony_users(user_list: List[SingleUser], sym_client: BotClient):
    success_users = []
    failed_users = {}

    for user in user_list:
        try:
            sym_id = onboard.sym_user_id_get(symphony_client=sym_client, email_address=user.email)

            if not sym_id:
                sym_id = onboard.sym_user_create(symphony_client=sym_client, firstname=user.first_name, lastname=user.last_name,
                                        email_address=user.email, company_name=user.company, title=user.title,
                                        department=user.department)

            if sym_id:
                user.symphony_id = sym_id
                success_users.append(user)
            else:
                failed_users[user] = 'Symphony API returned no user id. Presume user failed to create.'

        except api_ex.SymphonyException as ex:
            logging.exception(ex)

            failed_users[user] = f'Symphony exception when creating user: {str(ex)}'
        except Exception as ex:
            logging.exception(ex)

            failed_users[user] = f'General exception when creating user: {str(ex)}'

    return success_users, failed_users


def finalize_users(user_list, sym_client: BotClient, ibm: InfoBarrierManager):
    success_users = []
    failed_users = {}

    sponsor_dict = {}
    zendesk_orgs = {}

    for user in user_list:
        try:
            sponsor_id = user.sponsor_sfdc_id

            if sponsor_id in sponsor_dict:
                sponsor_name = sponsor_dict.get(sponsor_id)
            else:
                sponsor_name = onboard.sfdc_account_get_name(sponsor_id)
                sponsor_dict[sponsor_id] = sponsor_name

            user.sponsor_account_name = sponsor_name
        except Exception as ex:
            logging.exception(ex)
            failed_users[user] = 'Failed to obtain Sponsor Name from Salesforce'
            continue

        sfdc_err = ''
        try:
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
                    onboard.sfdc_contact_update_sym_id(contact_id=contact_id, sym_user_id=user.symphony_id)

                    onboard.sfdc_email_contact(email_address=user.email, contact_id=contact_id)
                else:
                    sfdc_err = 'Unable to create Contact - see Salesforce Logs'
            else:
                sfdc_err = 'Unable to create Account - see Salesforce Logs'
        except Exception as ex:
            logging.exception(ex)
            failed_users[user] = f'Failed creating Salesforce records. {sfdc_err}'
            continue

        # Symphony record creation
        try:
            ib_group_id = onboard.sym_ib_group_get(ib_client=ibm, company_name=user.company)

            if not ib_group_id:
                ib_group_id = onboard.sym_ib_group_create(ib_client=ibm, company_name=user.company)
                onboard.sym_ib_group_add_policies(ib_client=ibm, ib_group_id=ib_group_id)

            onboard.sym_ib_group_add_user(ib_client=ibm, ib_group_id=ib_group_id, sym_user_id=user.symphony_id)
        except Exception as ex:
            logging.exception(ex)
            failed_users[user] = f'Failed creating Symphony IB records. {sfdc_err}'
            continue

        # Zendesk record creation
        try:
            domain_name = user.email.split('@')[1]

            if user.company in zendesk_orgs:
                zen_org_id = zendesk_orgs[user.company]
            else:
                zen_org_id = onboard.zen_company_add(company_name=user.company, email_domain=domain_name,
                                                    sponsor_company_name=sponsor_name)
                zendesk_orgs[user.company] = zen_org_id

            if zen_org_id:
                onboard.zen_user_add(zendesk_org_id=zen_org_id, firstname=user.first_name, lastname=user.last_name,
                                     email_address=user.email)
        except Exception as ex:
            logging.exception(ex)
            failed_users[user] = f'Failed to add Zendesk entries for this user'

        success_users.append(user)

    return success_users, failed_users