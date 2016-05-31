import time
import json
import logging
import requests
from requests.exceptions import RequestException, ConnectionError
from threading import Thread
from collections import defaultdict
from urllib.parse import urljoin

from ssmanager import Server


TRAFFIC_CHECK_PERIOD = 30

class YaSSP():
    traffic_sync_threshold = 100 * 1024 * 1024  # 100 MiB
    traffic_sync_timeout = 60 * 30  # 30 mins

    def __init__(self, url_prefix, hostname, psk, manager):
        self._running = False
        self._synced_traffic = defaultdict(lambda: 0)
        self._last_active_time = {}

        self._url_prefix = url_prefix
        self._hostname = hostname
        self._psk = psk
        self._manager = manager

    def _request(self, func, path, **kwargs):
        req = func(urljoin(self._url_prefix, path),
                   params=dict(token=self._psk),
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
        try:
            profiles = self._get('list')
        except (RequestException, AuthenticationError, UnexpectedResponseError, ConnectionError) as e:
            logging.warning('Error on update profiles: %s' % e)
        logging.debug('Syncing %s profiles...' % len(profiles))
        servers = (Server(port=int(p['port']), password=p['passwd'],
                          method=p['method'], ota=p['ota']=='1')
                   for p in profiles)
        self._manager.update(servers)

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

            self._last_active_time[port] = time.time()

        if to_upload:
            logging.debug('Uploading traffic (%d/%d)...' % (len(to_upload), len(stat)))
            try:
                to_post = {'update': list(dict(port=p, transfer=t) for p, t in to_upload.items())}
                resp = self._post('updates', data=json.dumps(to_post))
                if resp.get('code') != 200:
                    raise UnexpectedResponseError('Code returned by server %s != 200.' % resp.get(200))
            except (RequestException, AuthenticationError, UnexpectedResponseError, ConnectionError) as e:
                logging.warning('Error on upload traffic: %s' % e)
            else:
                for port, __ in to_upload.items():
                    self._synced_traffic[port] = traffic

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

