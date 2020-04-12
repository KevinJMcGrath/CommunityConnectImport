class NewUserData:
    def __init__(self):
        self.first_name = ''
        self.last_name = ''
        self.email = ''
        self.username = ''
        self.domain = ''
        self.parent_username = ''
        self.keypair_record_id = ''
        self.rsa_public_key = ''
        self.company_name = ''


class DBUserSession:
    def __init__(self, sqlite_row):
        self.user_id = sqlite_row['user_id']
        self.session_token = sqlite_row['session_token']
        self.km_token = sqlite_row['km_token']
        self.rsa_id = sqlite_row['rsa_id']
        self.parent_id = sqlite_row['parent_id']
        self.username = sqlite_row['bot_username']
        self.expires = sqlite_row['expires']