import logging

from symphony.bot_client import BotClient


class InfoBarrierManager:
    def __init__(self, bot_client: BotClient):
        self.client = bot_client
        self.ib_policies = set()
        self.ib_groups = {}

        self.populate_existing_ib_groups()

        # This takes waaaaaaaaay too long coming back from the pod.
        # self.populate_existing_ib_policies()

    # def populate_existing_ib_policies(self):
    #     logging.info('Caching info barrier policies...')
    #     policy_resp = self.client.InfoBarriers.list_ib_policies()
    #
    #     for pol in policy_resp:
    #         key = f'{pol["groups"][0]}_{pol["groups"][0]}'
    #         self.ib_policies.add(key)

    def populate_existing_ib_groups(self, filter_prefix: str = None):
        logging.info('Caching info barrier groups...')
        group_resp = self.client.InfoBarriers.list_ib_groups()

        for g in group_resp['data']:
            if not g['active']:
                continue

            if filter_prefix:
                if g['name'].startswith(filter_prefix):
                    self.ib_groups[g['id']] = g['name']
            else:
                self.ib_groups[g['id']] = g['name']


    def is_existing_policy(self, ib_group_1_id: str, ib_group_2_id: str):
        key1 = f'{ib_group_1_id}_{ib_group_2_id}'
        key2 = f'{ib_group_2_id}_{ib_group_1_id}'

        return key1 in self.ib_policies or key2 in self.ib_policies


    def get_ib_group_id(self, group_name: str):
        if group_name in self.ib_groups.values():
            # Returns the key (ib group id) by value (ib group name)
            logging.info(f'IB Group {group_name} found in pod')

            return list(self.ib_groups.keys())[list(self.ib_groups.values()).index(group_name)]
        else:
            ib_group_id = self.create_ib_group(group_name)
            self.ib_groups[ib_group_id] = group_name

            return ib_group_id

    def get_existing_ib_group(self, group_name):
        if group_name in self.ib_groups.values():
            return list(self.ib_groups.keys())[list(self.ib_groups.values()).index(group_name)]

    def create_ib_group(self, group_name: str):
        return self.client.InfoBarriers.create_ib_user_group(group_name)['data']['id']

    def add_users_to_ib_group(self, group_id: str, user_ids: list):
        self.client.InfoBarriers.add_users_to_ib_group(group_id, user_ids)

    def create_ib_group_policy(self, group_1_id: str, group_2_id: str):
        return self.client.InfoBarriers.create_ib_policy(group_1_id, group_2_id)['data']['id']

    def create_all_policy_combinations(self, new_group_id: str):
        added_policy_count = 0
        existing_policy_count = 0
        for group_id in self.ib_groups:
            if new_group_id != group_id and not self.is_existing_policy(group_id, new_group_id):
                try:
                    self.client.InfoBarriers.create_ib_policy(new_group_id, group_id)
                    key = f'{new_group_id}_{group_id}'
                    self.ib_policies.add(key)
                    added_policy_count += 1
                except Exception as ex:
                    existing_policy_count += 1
                    continue

        logging.info(f'Created {added_policy_count} new Info Barrier policies. Policies already in place: {existing_policy_count}')