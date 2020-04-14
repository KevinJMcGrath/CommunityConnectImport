import symphony.utility as util


def session_auth_cert():
    return '/sessionauth/v1/authenticate'


def km_auth_cert():
    return '/keyauth/v1/authenticate'


def session_auth_jwt():
    return '/login/pubkey/authenticate'


def km_auth_jwt():
    return '/relay/pubkey/authenticate'


def session_auth_obo_app():
    return '/sessionauth/v1/app/authenticate'


def session_auth_obo_user(user_id: str):
    return f'/sessionauth/v1/app/user/{user_id}/authenticate'


def echo():
    return 'agent/v1/util/echo'


def create_im(exclude_bot: bool = False):
    im_ep = 'pod/v1/'
    im_ep += 'admin/' if exclude_bot else ''
    im_ep += 'im/create'

    return im_ep


def send_message(stream_id: str, version: int=2):
    s_id = util.format_symphony_stream_id(stream_id)
    return f'agent/v{str(version)}/stream/{s_id}/message/create'


def create_user():
    return f'pod/v2/admin/user/create'


def lookup_user_list(user_emails: list, local_users_only: bool):
    qs = ','.join(user_emails)
    return f'pod/v3/users?local={str(local_users_only).lower()}&email={qs}'


def lookup_user(user_email: str, local_users_only: bool = True):
    return f'pod/v3/users?local={str(local_users_only).lower()}&email={user_email}'


def search_user(local_users_only: bool):
    return f'pod/v1/user/search?local={str(local_users_only).lower()}'


def find_user():
    return 'pod/v1/admin/user/find'


def add_user_to_stream(stream_id: str):
    s_id = util.format_symphony_stream_id(stream_id)
    return f'pod/v1/room/{s_id}/membership/add'


def promote_user_to_owner(stream_id: str):
    s_id = util.format_symphony_stream_id(stream_id)
    return f'pod/v1/room/{s_id}/membership/promoteOwner'


def list_user_groups(type: str):
    return f'pod/v2/admin/usergroups?type={type}'


def search_room(result_limit: int = 0):
    suffix = '/pod/v3/room/search'

    if result_limit > 0:
        suffix += '?limit=' + str(result_limit)

    return suffix


def create_room():
    return '/pod/v2/room/create'


def list_user_streams(limit: int = 50, skip: int = 0):
    return f'pod/v1/streams/list?limit={limit}&skip={skip}'


def set_presence():
    return 'pod/v2/user/presence'


def update_user_features(user_id: str):
    return f'pod/v1/admin/user/{user_id}/features/update'


def list_users(limit: int = 1000, skip_count: int = 0):
    return f'pod/v2/admin/user/list?limit={limit}&skip={skip_count}'


def list_ib_groups():
    return f'webcontroller/admin/v2/groups/'


def list_ib_policies():
    return f'pod/v1/admin/policy/list'


def create_ib_group():
    return f'webcontroller/admin/v2/groups'


def add_user_ib_group(group_id: str):
    return f'pod/v1/admin/group/{group_id}/membership/add'


def create_ib_policy():
    return f'webcontroller/admin/v2/policies'