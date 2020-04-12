import symphony.rest.endpoints as sym_ep

from symphony.api_base import APIBase


class Admin(APIBase):
    def __init__(self, session):
        super().__init__(session)

    def update_user_features(self, user_id: str, features: list):
        """
        :param user_id: str
            Symphony user Id
        :param features: list(dict)
            List of features to be actioned for the user. Each feature should be specified as follows:
            {
                "entitlement": "myEntitlementName",
                "enabled": True (False)
            }
        """

        ep = self.get_endpoint(sym_ep.update_user_features(user_id))

        return self.post(ep, features)

    def list_users(self):
        ep = self.get_endpoint(sym_ep.list_users())

        return self.get(ep)
