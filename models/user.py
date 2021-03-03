class SingleUser:
    def __init__(self, api_payload):
        # required fields
        self.first_name = api_payload.get('firstname')
        self.last_name = api_payload.get('lastname')
        self.email = api_payload.get('email')
        self.company = api_payload.get('company_name')
        self.sponsor_sfdc_id = api_payload.get('sponsor_id')

        self.phone = api_payload.get('phone')
        self.department = api_payload.get('department')
        self.title = api_payload.get('title', '')
        self.region = api_payload.get('region', 'AMER')
        self.is_compliance = api_payload.get('is_compliance_officer', False)
        self.is_support = api_payload.get('is_support_contact', False)

        self.sfdc_id = ''
        self.sfdc_account_id = ''
        self.symphony_id = ''
        self.password_set = None
        self.sponsor_account_name = ''

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
        self.is_compliance = csv_row.get('IsComplianceOfficer', 'FALSE').strip()
        self.is_support = csv_row.get('IsSupportContact').strip()
        self.sponsor_sfdc_id = self.get_sfdc_id(csv_row)
        self.sfdc_id = ""
        self.sfdc_account_id = ""
        self.symphony_id = ""
        self.password_set = None
        self.existing_user_flag: bool = False

    def is_valid(self):
        return self.first_name and self.last_name and self.email and self.company and self.sponsor_sfdc_id

    def get_sfdc_id(self, row):
        if 'SponsorsSFDCid' in row:
            return row.get('SponsorsSFDCid').strip()
        elif 'SFDCid' in row:
            return row.get('SFDCid').strip()
        else:
            return None