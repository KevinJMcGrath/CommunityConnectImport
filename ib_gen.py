from utility import timeit
from symphony.bot_client import BotClient

ib_policies = set()
ib_groups = {}


# create a set of existing IB policies to check against to see if the policy already exists.
def populate_existing_ib_policies(bot_client: BotClient):
    print('Obtaining current IB policy list from POD...', end='')
    policy_resp = bot_client.InfoBarriers.list_ib_policies()

    for pol in policy_resp:
        key = f'{pol["groups"][0]}_{pol["groups"][0]}'
        ib_policies.add(key)

    print('done!')


def populate_existing_ib_groups(bot_client: BotClient, filter_prefix: str = None):
    print('Obtaining current IB group list from POD...', end='')
    group_resp = bot_client.InfoBarriers.list_ib_groups()

    for g in group_resp['data']:
        if not g['active']:
            continue

        if filter_prefix:
            if g['name'].startswith(filter_prefix):
                ib_groups[g['id']] = g['name']
        else:
            ib_groups[g['id']] = g['name']


def is_existing_policy(ib_group_1_id: str, ib_group_2_id: str):
    key1 = f'{ib_group_1_id}_{ib_group_2_id}'
    key2 = f'{ib_group_2_id}_{ib_group_1_id}'

    return key1 in ib_policies or key2 in ib_policies

def create_ib_group(group_name: str, bot_client: BotClient):
    return bot_client.InfoBarriers.create_ib_user_group(group_name)['data']['id']


# This call could be time consuming
def add_users_to_ib_group(group_id: str, user_ids: list, bot_client: BotClient):
    bot_client.InfoBarriers.add_users_to_ib_group(group_id, user_ids)

def create_ib_group_policy(group_1_id: str, group_2_id: str, bot_client: BotClient):
    return bot_client.InfoBarriers.create_ib_policy(group_1_id, group_2_id)['data']['id']

def create_all_policy_combinations(new_group_id: str, bot_client: BotClient):
    policy_count = 0
    for group_id in ib_groups:
        if new_group_id != group_id and not is_existing_policy(group_id, new_group_id):
            try:
                bot_client.InfoBarriers.create_ib_policy(new_group_id, group_id)
                key = f'{new_group_id}_{group_id}'
                ib_policies.add(key)
                policy_count += 1
            except Exception:
                continue

    print(f'Created {policy_count} new Info Barrier policies.')
