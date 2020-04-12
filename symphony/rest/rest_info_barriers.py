import symphony.rest.endpoints as sym_ep

from symphony.api_base import APIBase


class InfoBarriers(APIBase):
    def __init__(self, session):
        super().__init__(session)

    def list_ib_groups(self):
        ep = self.get_endpoint(sym_ep.list_ib_groups())

        return self.get(ep)

    def list_ib_policies(self):
        ep = self.get_endpoint(sym_ep.list_ib_policies())

        return self.get(ep)

    def create_ib_user_group(self, group_name: str):
        ep = self.get_endpoint(sym_ep.create_ib_group())
        payload = {
            "data": {
                "name": group_name
            }
        }

        response = self.post(ep, payload)
        return response

    def create_ib_policy(self, group_1_id: str, group_2_id: str):
        ep = self.get_endpoint(sym_ep.create_ib_policy())
        payload = {
            "data": {
                "active": True,
                "policyType": "BLOCK",
                "groupIds": [group_1_id, group_2_id]
            }
        }

        return self.post(ep, payload)

    def add_users_to_ib_group(self, group_id: str, user_ids: list):
        ep = self.get_endpoint(sym_ep.add_user_ib_group(group_id))
        self.post(ep, user_ids)