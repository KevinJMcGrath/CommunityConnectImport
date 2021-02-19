from models.user import SingleUser

required_params = ['firstname', 'lastname', 'email', 'phone', 'department', 'sponsor_sfdc_id', 'company']

def import_single_user(payload):
    user = SingleUser(payload)

    # 1. Check for existing Account in SFDC

    # 2. Create/Update SFDC Account

    # 3. Check for existing Contact in SFDC

    # 4. Create/Update SFDC Contact

    # 5. Check for existing user in Symphony

    # 6. Add user to Symphony

    # 7. Add IB Group for company

    # 8. Add IB Rules

    # 9. Check for existing company in Zendesk

    # 10. Create/Update user in Zendesk

    # 11. Check for existing user in Zendesk

    # 12. Create/Update user in Zendesk

    # 13. Email user

    # 14. Email onboarding/support
