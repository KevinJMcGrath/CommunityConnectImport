import logging

from typing import List

from ib_gen import InfoBarrierManager
from symphony import BotClient
from models.user import ImportedUser


logging.getLogger()

def onboard_users(user_dict: dict, bot_client: BotClient):
    ibm = InfoBarrierManager(bot_client)

    for group_name, user_list in user_dict.items():
        group_name = f"cc_{group_name}"

        # Find IB group Id or create if new
        ib_group_id = ibm.get_ib_group_id(group_name)

        # Onboard users
        user_ids = insert_users(user_list, bot_client)

        # Add users to IB group
        ibm.add_users_to_ib_group(ib_group_id, user_ids)

        # Add IB Policies
        ibm.create_all_policy_combinations(ib_group_id)


def insert_users(user_list: List[ImportedUser], bot_client: BotClient):
    user_id_list = []
    for user in user_list:
        user_id = bot_client.User.lookup_user_id(user.email)

        if not user_id:
            # Insert new user into Symphony
            logging.info(f'Creating user for email {user.email}')
            sym_user = bot_client.User.create_symphony_user(user.first_name, user.last_name, user.email,
                                                           user.email, user.company, title=user.title,
                                                            department=user.department, password_set=user.password_set)
            user_id = sym_user['userSystemInfo']['id']
        else:
            logging.info(f'User {user.email} already exsits on pod ({user_id})')

        user.symphony_id = user_id
        user_id_list.append(user_id)

    return user_id_list


# for each company requested, do the following:
# 1. create the parent user in symphony
# 2. add parent user to database
# 3. for each user_per_company, create user in symphony
# 4. add each user_per_company to database
# 5. get list of all existing IB groups on pod
# 6. create IB group for each parent user (name "cusc_" + {parent_user_id})
# 7. add parent and all children to IB group
# for each new IB group:
# 8. add IB policy for each group id in existing list
# 9. add IB group to existing IB group list
# 10. goto 8.