
import config
import salesforce

from models.user import SingleUser
from symphony.bot_client import BotClient

# FirstName,LastName,EmailAddress,CompanyName,Phone Number,Department,Title,UserRegion,IsComplianceOfficer,IsSupportContact,SponsorsSFDCid
required_params = ['firstname', 'lastname', 'email', 'phone', 'department', 'sponsor_sfdc_id', 'company']

def import_single_user(payload):
    is_success, err = verify_payload(payload)

    if not is_success:
        return False, err

    user = SingleUser(payload)
    is_success, err = salesforce.import_salesforce_single_user(user)

    if not is_success:
        return False, err




    return is_success, err


def verify_payload(payload):
    for param in required_params:
        if not payload.get(param):
            return False, f'{param} is required.'

    return True, None