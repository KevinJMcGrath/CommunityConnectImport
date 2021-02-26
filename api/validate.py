import logging

import config

from models.user import SingleUser


# FirstName,LastName,EmailAddress,CompanyName,Phone Number,Department,Title,UserRegion,IsComplianceOfficer,IsSupportContact,SponsorsSFDCid
req_fields = ['firstname', 'lastname', 'email', 'sponsor_id', 'company_name']

async def validate_single_payload(api_request) -> (bool, list):
    """
    :param api_request: Inbound request object containing the Community Connect user details.
        The following fields are required:
            firstname
            lastname
            email
            sponsor_id
            company_name
        The following fields are optional:
            phone
            department
            title
            is_support_contact
            is_compliance_officer
    :return: Returns a (bool, list) tuple.
        success: The payload was validated
        error_list: If the payload has validation errors, they are contained here and can be passed to the client
    """
    success = True

    err_msg = ''
    missing_fields = []
    missing_values = []

    payload = await api_request.get_json()

    if not payload:
        logging.error('Inbound payload empty. Cannot proceed with user creation.')
        return False


    is_valid = True
    for field_name in req_fields:
        if field_name not in payload:
            missing_fields.append(field_name)
            is_valid = False
        elif not payload[field_name]:
            missing_values.append(field_name)
            is_valid = False

    if missing_fields:
        err_msg = "The following fields are missing from the payload: {','.join(missing_fields)}"
    elif missing_values:
        err_msg = f"The following fields are missing values: {','.join(missing_values)}"

    if is_valid:
        return SingleUser(payload)
    else:
        logging.error(err_msg)
        return False


def validate_api_key(api_request):
    api_key = api_request.headers.get('X-SYM-COMCON')

    if not api_key or api_key.lower() != config.api_key.lower():
        return False

    return True