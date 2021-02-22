import logging

import config

from integration import salesforce
from integration import sendgrid as sg
from integration import zendesk as zen
from models.user import SingleUser
from symphony.bot_client import BotClient
from symphony.ib_gen import InfoBarrierManager


def import_single_user(payload):
    try:
        user = SingleUser(payload)
        sym_client = BotClient(config.bot_config)
        ibm = InfoBarrierManager(sym_client)
        domain = user.email.split('@')[1].lower()

        # 1. Check for existing Account in SFDC
        # 2. Create/Update SFDC Account
        account_id = salesforce.get_company_id(user.company)
        salesforce.update_company_sponsor(company_id=account_id, sponsor_id=user.sponsor_sfdc_id)

        # 3. Check for existing Contact in SFDC
        contact_id = salesforce.contact_query(user.email)

        # 4. Create/Update SFDC Contact
        if not contact_id:
            contact_id = salesforce.insert_contact(account_id=account_id, firstname=user.first_name,
                                                   lastname=user.last_name, email=user.email)


        # 5. Check for existing user in Symphony
        sym_user_id = sym_client.User.lookup_user_id(user.email)

        # 6. Add user to Symphony
        if not sym_user_id:
            sym_user_id = sym_client.User.create_symphony_user(user.first_name, user.last_name, user.email,
                                                 user.email, user.company, title=user.title,
                                                 department=user.department)

        salesforce.update_contact_symphony_id(contact_id, sym_user_id)

        # 7. Add IB Group for company
        cname = user.company.strip().replace(' ', '_')
        group_name = f"cc_{cname}"
        ib_group_id = ibm.get_ib_group_id(group_name)

        # 8. Add User to IB Group
        ibm.add_users_to_ib_group(group_id=ib_group_id, user_ids=[sym_user_id])

        # 9. Add IB policy combinations
        ibm.create_all_policy_combinations(ib_group_id)

        # 10. Create/Update user in Zendesk
        sponsor_company_name = salesforce.get_account_name_by_id(user.sponsor_sfdc_id)
        zen_company = zen.get_or_add_org(user.company, domain=domain, sponsor_name=sponsor_company_name)
        zen_company_id = zen_company.id

        # 11. Create/Update user in Zendesk
        zen_user = zen.get_or_add_user(fullname=f'{user.first_name} {user.last_name}', email=user.email,
                                          org_id=zen_company_id)

        # 13. Email user
        salesforce.send_single_welcome_email(email=user.email, contact_id=contact_id)

        # 14. Email onboarding/support
        # sg.send_email(from_address='kevin.mcgrath@symphony.com', to_addresses=[''])

        return True, None
    except Exception as ex:
        logging.exception(ex)
        return False, str(ex)
