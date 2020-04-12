import symphony.session

from symphony.rest.rest_admin import Admin
from symphony.rest.rest_info_barriers import InfoBarriers
from symphony.rest.rest_user import User


class BotClient:
    """
    Creates a client associated with a Symphony service user account.
    """
    def __init__(self, symphony_config: dict):
        self.config = symphony_config
        self.session = symphony.session.Session(self.config)

        self.Admin = Admin(self.session)
        self.InfoBarriers = InfoBarriers(self.session)
        self.User = User(self.session)
