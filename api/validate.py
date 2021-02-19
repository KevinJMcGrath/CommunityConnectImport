
# FirstName,LastName,EmailAddress,CompanyName,Phone Number,Department,Title,UserRegion,IsComplianceOfficer,IsSupportContact,SponsorsSFDCid
req_fields = ['firstname', 'lastname', 'email', 'sponsor_id', 'company_name']

def validate_payload(inbound_json: dict) -> (bool, list):
    """
    :param inbound_json: Inbound JSON payload containing the Community Connect user details.
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

    missing_fields = []
    missing_values = []
    for field_name in req_fields:
        if field_name not in inbound_json:
            missing_fields.append(field_name)
        elif not inbound_json[field_name]:
            missing_values.append(field_name)

    error_list = []

    if missing_fields:
        error_list.append(f"The following fields are missing from the payload: {','.join(missing_fields)}")

    if missing_values:
        error_list.append(f"The following fields are missing values: {','.join(missing_values)}")

    return success, error_list