#!/usr/bin/env python3
import os
import sys
import time
import signal
import logging
from os.path import isfile
from configparser import ConfigParser
from ssmanager import Server
from ssmanager.sslibev import Manager as ManagerEv
from ssmanager.sspy import Manager as ManagerPy

from .yassp import YaSSP
from . import pushserver, utils


def get_config():
    if len(sys.argv) != 2:
        print('Usage:\n\t%s <PATH-TO-CONFIG-FILE>' % sys.argv[0])
        sys.exit(1)
    path = sys.argv[1]
    if not isfile(path):
        print('Error: config file "%s" not exist.' % path)
        sys.exit(1)
    config = ConfigParser()
    config.read(path)
    return config['DEFAULT']

def exit(signalnum, frame):
    logging.info('Stopping by SIGTERM/SIGHUP.')
    sys.exit()

def main():
    conf = get_config()
    logging.basicConfig(level=conf.getint('log level'),
                        format='%(asctime)s %(levelname)-s: %(message)s')
    utils.ss_bind_address = conf['ss-server bind']
    ss_type = conf['ss daemon type']
    if ss_type == 'libev':
        Manager = ManagerEv
    elif ss_type == 'python':
        Manager = ManagerPy
    else:
        logging.critical('Unknown "ss daemon type" %s, must be "libev" or "python"', ss_type)
        sys.exit(1)
    manager = Manager(ss_bin=conf['ss-server path'],
                      print_ss_log=conf.getboolean('ss-server print log'))

    yassp_type = conf.get('yassp type', 'nico')
    yassp = YaSSP(yassp_type, conf['yassp url'], conf['yassp hostname'],
                  conf['yassp psk'], manager)
    yassp.traffic_sync_threshold = conf.getint('traffic sync threshold')
    yassp.traffic_sync_timeout = conf.getint('traffic sync timeout')
    signal.signal(signal.SIGTERM, exit)
    signal.signal(signal.SIGHUP, exit)

    try:
        manager.start()
        yassp.start()
        if conf.getboolean('push server enable'):
            pushserver.run(manager, conf['push token'],
                           host=conf['push bind address'],
                           port=conf.getint('push bind port'))
        else:
            yassp._listen_thread.join()
    except KeyboardInterrupt:
        logging.info('Stopping by ^C.')
    finally:
        yassp.stop()
        manager.stop()
        logging.info('Exited.')

if __name__ == '__main__':
    main()

