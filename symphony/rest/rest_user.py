from base64 import b64encode

import config
import symphony.rest.endpoints as sym_ep

from models.security import Passwords
from symphony.api_base import APIBase


class User(APIBase):
    def __init__(self, session):
        super().__init__(session)

    def lookup_user_id(self, email: str):
        ep = self.get_endpoint(sym_ep.lookup_user(email))

        user_list = self.get(ep)

        if user_list:
            return user_list['users'][0]['id']
        else:
            return None

    def list_user_groups(self):
        ep = self.get_endpoint(sym_ep.list_user_groups("ROLE_SCOPE"))

        return self.get(ep)

    def create_symphony_user(self, first_name: str, last_name: str, email: str, username: str, company_name: str,
                             password_set: Passwords = None):
        user = {
            "userAttributes": {
                "accountType": "NORMAL",
                "emailAddress": email,
                "firstName": first_name[:64],
                "lastName": last_name[:64],
                "displayName": f"{first_name[:64]} {last_name[:64]} ({company_name})",
                "userName": username,
                # This must ALWAYS be one of the pre-defined values on the pod.
                "companyName": config.pod_company_name,
            },
            "roles": ["INDIVIDUAL"]
        }

        if password_set:
            ps = {
                "hSalt": b64encode(password_set.user_password_salt).decode('utf-8'),
                "hPassword": b64encode(password_set.user_password_hash).decode('utf-8'),
                "khSalt": b64encode(password_set.km_password_salt).decode('utf-8'),
                "khPassword": b64encode(password_set.km_password_hash).decode('utf-8')
            }

            user["password"] = ps

        ep = self.get_endpoint(sym_ep.create_user())

        return self.post(ep, user)

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