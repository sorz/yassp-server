import time
import json
import logging
import requests
from threading import Thread
from collections import defaultdict
from urllib.parse import urljoin

from ssmanager import Server


TRAFFIC_CHECK_PERIOD = 30

class YaSSP():
    _running = False
    _synced_traffic = defaultdict(lambda: 0)
    _last_active_time = {}
    traffic_sync_threshold = 100 * 1024 * 1024  # 100 MiB
    traffic_sync_timeout = 60 * 30  # 30 mins

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
            raise AuthenticationError()
        elif req.status_code == 200:
            return req.json()
        elif req.status_code == 204:
            return
        else:
            raise UnexpectedResponseError()

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
        profiles = self._get('profiles/all/')
        logging.debug('Syncing %s profiles...' % len(profiles))
        self._manager.update(Server(**p) for p in profiles)

    def update_traffic(self):
        stat = self._manager.stat()
        to_upload = {}
        for port, traffic in stat.items():
            increment = traffic - self._synced_traffic[port]
            if increment == 0:
                continue
            if increment < 0:
                self._synced_traffic[port] = 0
                increment = traffic

            if time.time() - self._last_active_time.get(port, 0) > self.traffic_sync_threshold \
               or increment >= self.traffic_sync_threshold:
                to_upload[port] = increment
                # TODO: only update synced traffic after request sent successfully.
                self._synced_traffic[port] = traffic

            self._last_active_time[port] = time.time()

        if to_upload:
            logging.debug('Uploading traffic (%d/%d)...' % (len(to_upload), len(stat)))
            self._post('traffics/update/', data=json.dumps(to_upload))

    def _listen_profile_changes(self):
        # Currently, we just fetch all profiles every 5 minutes.
        while self._running:
            time.sleep(60 * 5)
            self.update_profiles()

    def _traffic_timer(self):
        while self._running:
            time.sleep(min(TRAFFIC_CHECK_PERIOD, self.traffic_sync_timeout))
            self.update_traffic()


class AuthenticationError(Exception):
    pass

class UnexpectedResponseError(Exception):
    pass

