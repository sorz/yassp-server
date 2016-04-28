import requests
from urllib.parse import urljoin


class YaSSP():
    def __init__(self, url_prefix, hostname, psk):
        self._url_prefix = url_prefix
        self._hostname = hostname
        self._psk = psk

    def _request(self, func, path, **kwargs):
        req = func(urljoin(self._url_prefix, path),
                   auth=(self._hostname, self._psk),
                   **kwargs)
        if req.status_code == 403:
            raise AuthenticationError
        elif req.status_code == 200:
            return req.json()
        else:
            raise UnexpectedResponseError

    def _get(self, *args, **kwargs):
        return self._request(requests.get, *args, **kwargs)

    def _post(self, *args, **kwargs):
        return self._request(requests.post, *args, **kwargs)

    def get_all_profiles(self):
        return self._get('profiles/all/')


class AuthenticationError(Exception):
    pass

class UnexpectedResponseError(Exception):
    pass

