import jsonpickle
import logging
import requests

from .session import Session


class APIBase:
    def __init__(self, current_session: Session):
        self.session = current_session

        self.api_base_url = self.session.config['api_host'] + ':' + self.session.config['api_port'] + '/'

    def get_endpoint(self, symphony_endpoint: str):
        return self.api_base_url + symphony_endpoint

    def post(self, endpoint: str, body):
        return self.rest_callout('post', endpoint, body)

    def get(self, endpoint: str):
        return self.rest_callout('get', endpoint)

    def rest_callout(self, method, endpoint, body_object=None):
        self.session.authenticate()

        response = None
        status_code = None
        message = None

        try:
            if method.lower() == 'get':
                response = self.session.http_session.get(endpoint, headers=self.session.get_rest_headers())
            elif method.lower() == 'post':
                body_str = jsonpickle.encode(body_object, unpicklable=False)
                response = self.session.http_session.post(endpoint, data=body_str, headers=self.session.get_rest_headers())

            status_code = response.status_code
            if response.status_code // 100 != 2:
                response.raise_for_status()

            # UGH Sometimes Symphony endpoints return nothing instead of empty JSON
            if response.text:
                return jsonpickle.decode(response.text)
            else:
                return None

        except requests.exceptions.HTTPError as http_ex:
            logging.error(http_ex)

            if http_ex.response and http_ex.response.text:
                logging.error(http_ex.response.text)

            raise http_ex
        except requests.exceptions.ConnectionError as conn_ex:
            logging.error(conn_ex)
            raise conn_ex
        except Exception as ex:
            logging.error(ex)
            raise ex
