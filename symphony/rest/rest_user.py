import symphony.rest.endpoints as sym_ep

from utility import timeit
from symphony.api_base import APIBase


class User(APIBase):
    def __init__(self, session):
        super().__init__(session)

    def list_user_groups(self):
        ep = self.get_endpoint(sym_ep.list_user_groups("ROLE_SCOPE"))

        return self.get(ep)

    @timeit
    def create_service_user(self, first_name: str, last_name: str, email: str, username: str, company_name: str,
                            public_key: str):
        # Service users do not get firstName or lastName. I don't know why they thought that was
        # important enough to validate, but they did. Thanks guys.
        user = {
            "userAttributes": {
                "accountType": "SYSTEM",
                "emailAddress": email,
                # "firstName": first_name[:64],
                # "lastName": last_name[:64],
                "displayName": f"{first_name[:64]} {last_name[:64]}",
                "userName": username,
                "companyName": company_name,
                "currentKey": {"key": public_key}
            },
            "roles": ["INDIVIDUAL"]
        }

        # for key, value in kwargs.items():
        #     user["userAttributes"][key] = value

        ep = self.get_endpoint(sym_ep.create_user())

        return self.post(ep, user)

    # required fields for user insert:
    # emailAddress
    # firstName
    # lastName
    # userName
    # displayName
    # companyName
    # roles