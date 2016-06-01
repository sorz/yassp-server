from bottle import get, post, request, abort
from io import TextIOWrapper
import bottle
import json
import logging

from .utils import parse_servers


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
    logging.debug('Syncing %s profiles (push)...' % len(profiles))
    manager.update(parse_servers(profiles))

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

