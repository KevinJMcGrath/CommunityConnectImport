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

class SingleUser:
    def __init__(self, api_payload):
        self.first_name = api_payload.get('firstname')
        self.last_name = api_payload.get('lastname')
        self.email = api_payload.get('email')
        self.company = api_payload.get('company')
        self.phone = api_payload.get('phone')
        self.department = api_payload.get('department')
        self.title = api_payload.get('title', '')
        self.region = api_payload.get('region', 'AMER')
        self.is_compliance = api_payload.get('is_compliance_officer', False)
        self.is_support = api_payload.get('is_support_contact', False)
        self.sponsor_sfdc_id = api_payload.get('sponsor_sfdc_id')
        self.sfdc_id = ""
        self.sfdc_account_id = ""
        self.symphony_id = ""
        self.password_set = None

class ImportedUser:
    def __init__(self, csv_row):
        self.first_name = csv_row.get('FirstName').strip()
        self.last_name = csv_row.get('LastName').strip()
        self.email = csv_row.get('EmailAddress').strip()
        self.company = csv_row.get('CompanyName').strip()
        self.phone = csv_row.get('Phone Number').strip()
        self.department = csv_row.get('Department').strip()
        self.title = csv_row.get('Title').strip()
        self.region = csv_row.get('UserRegion').strip()
        self.is_compliance = csv_row.get('IsComplianceOfficer').strip()
        self.is_support = csv_row.get('IsSupportContact').strip()
        self.sponsor_sfdc_id = csv_row.get('SponsorsSFDCid').strip()
        self.sfdc_id = ""
        self.sfdc_account_id = ""
        self.symphony_id = ""
        self.password_set = None
        self.existing_user_flag: bool = False

    def is_valid(self):
        return self.first_name and self.last_name and self.email and self.company and self.sponsor_sfdc_id