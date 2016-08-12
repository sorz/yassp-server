from bottle import get, post, request, abort, response
from io import TextIOWrapper
import bottle
import json
import logging

from .utils import parse_servers_moyu


token = 'test123'

def _check_token():
    if request.query.token != token:
        abort(401, 'No token given or invaild token.')

@get('/')
def home():
    _check_token()
    return 'It works.'

@post('/instances')
def update_instances():
    _check_token()
    profiles = json.load(TextIOWrapper(request.body))
    logging.debug('Syncing %s profiles (push)...' % len(profiles))
    # TODO: add support for nico
    manager.update(parse_servers_moyu(profiles))
    response.status = 204

def run(ssmanager, key, *args, **kwargs):
    global token, manager
    token = key
    manager = ssmanager
    logging.info('Starting push server...')
    bottle.run(*args, **kwargs)

def main():
    bottle.run(host='0.0.0.0', port=8080, reloader=True)

if __name__ == '__main__':
    main()

