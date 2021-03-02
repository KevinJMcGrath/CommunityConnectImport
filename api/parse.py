from models.user import SingleUser

def parse_single_user(payload):
    return SingleUser(payload)


def parse_bulk_users(payload):
    sponsor_id = payload.get('sponsor_id')

    user_list = []
    for u in payload:
        user_list.append(SingleUser(u))