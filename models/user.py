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


class ImportedUser:
    def __init__(self, csv_row):
        self.first_name = csv_row.get('FirstName')
        self.last_name = csv_row.get('LastName')
        self.email = csv_row.get('EmailAddress')
        self.company = csv_row.get('CompanyName')
        self.phone = csv_row.get('Phone')
        self.department = csv_row.get('Department')
        self.title = csv_row.get('Title')
        self.region = csv_row.get('UserRegion')
        self.is_compliance = csv_row.get('IsComplianceOfficer')
        self.is_support = csv_row.get('IsSupportContact')
        self.sponsor_sfdc_id = csv_row.get('SponsorSFDCId')
        self.sfdc_id = ""
        self.sfdc_account_id = ""
        self.symphony_id = ""
        self.password_set = None

    def is_valid(self):
        return self.first_name and self.last_name and self.email and self.company and self.sponsor_sfdc_id