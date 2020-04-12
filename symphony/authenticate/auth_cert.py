import jsonpickle
import requests

from datetime import datetime, timedelta

from symphony.rest import endpoints


def get_auth_token(endpoint, cert_path: str, key_path: str):
    response = requests.post(endpoint, cert=(cert_path, key_path))

    if response.status_code == 200:
        resp_json = jsonpickle.decode(response.text)
        return resp_json['token']

    response.raise_for_status()


def authenticate_bot(base_url: str, cert_path: str, key_path: str):
    session_ep = base_url + endpoints.session_auth_cert()
    km_ep = base_url + endpoints.km_auth_cert()

    session_token = get_auth_token(session_ep, cert_path, key_path)
    km_token = get_auth_token(km_ep, cert_path, key_path)
    expires = datetime.now() + timedelta(days=7)

    return session_token, km_token, expires
