from integration import salesforce

import config

from models.user import SingleUser
from symphony.bot_client import BotClient
from symphony.ib_gen import InfoBarrierManager

def import_single_user(payload):
    user = SingleUser(payload)
    sym_client = BotClient(config.bot_config)
    ibm = InfoBarrierManager(sym_client)

    # 1. Check for existing Account in SFDC
    # 2. Create/Update SFDC Account
    account_id = salesforce.get_company_id(user.company)

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

    # 7. Add IB Group for company
    cname = user.company.strip().replace(' ', '_')
    group_name = f"cc_{cname}"
    ib_group_id = ibm.get_ib_group_id(group_name)

    # 8. Add IB Rules
    ibm.add_users_to_ib_group(group_id=ib_group_id, user_ids=[sym_user_id])

    # 9. Check for existing company in Zendesk

    # 10. Create/Update user in Zendesk

    # 11. Check for existing user in Zendesk

    # 12. Create/Update user in Zendesk

    # 13. Email user

    # 14. Email onboarding/support
