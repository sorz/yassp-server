import time
import logging
import requests
from threading import Thread
from urllib.parse import urljoin

from ssmanager import Server


TRAFFIC_CHECK_PERIOD = 30

class YaSSP():
    _running = False

    def __init__(self, url_prefix, hostname, psk, manager):
        self._url_prefix = url_prefix
        self._hostname = hostname
        self._psk = psk
        self._manager = manager

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

    def start(self):
        self._manager.start()
        self._listen_thread = Thread(target=self._listen_profile_changes, daemon=True)
        self._traffic_thread = Thread(target=self._traffic_timer, daemon=True)
        self._running = True
        self.update_profiles()
        self._listen_thread.start()
        self._traffic_thread.start()

    def stop(self):
        self._running = False
        self._manager.shutdown()

    def update_profiles(self):
        servers = []
        profiles = self._get('profiles/all/')
        logging.debug('Syncing %s profiles...' % len(profiles))
        for profile in profiles:
            pid = profile.pop('pid')
            server = Server(**profile)
            server.pid = pid
        self._manager.update(servers)

    def update_traffic(self):
        pid_traffic = 'TODO'  # TODO
        self._post('traffic/update/', data=json.dumps(pid_traffic))

    def _listen_profile_changes(self):
        # Currently, we just fetch all profiles every 5 minutes.
        while self._running:
            time.sleep(60 * 5)
            self.update_profiles()

    def _traffic_timer(self):
        while self._running:
            time.sleep(TRAFFIC_CHECK_PERIOD)
            self.update_traffic()


class AuthenticationError(Exception):
    pass

class UnexpectedResponseError(Exception):
    pass

