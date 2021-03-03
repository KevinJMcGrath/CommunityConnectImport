from models.user import SingleUser

def parse_single_user(payload):
    return SingleUser(payload)


def parse_bulk_users(payload):
    sponsor_id = payload.get('sponsor_id')

    user_list = []
    for u in payload:
        su = SingleUser(u)

        # Allow for specifying sponsor Id as part of each user, so we can do multiple sponsors at once
        if not su.sponsor_sfdc_id:
            su.sponsor_sfdc_id = sponsor_id

        user_list.append(su)

    return user_list