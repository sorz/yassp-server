#!/usr/bin/env python3
import time
import logging
from argparse import ArgumentParser

from ssmanager import Manager, Server
from .yassp import YaSSP


def get_args():
    parser = ArgumentParser(description='YaSSP-Server')
    parser.add_argument('-S', '--ss-bin',
                        default='/usr/bin/ss-server',
                        metavar='PATH-TO-SS-SERVER')
    parser.add_argument('-P', '--print-ss-log',
                        action='store_true')
    parser.add_argument('-v', '--log-level',
			default=logging.INFO, type=int,
			metavar='LOG-LEVEL',
			help="1 to 50. Default 20, debug 10, verbose 5.")
    return parser.parse_args()


def main():
    args = get_args()
    logging.basicConfig(level=args.log_level,
                        format='%(asctime)s %(levelname)-s: %(message)s')
    manager = Manager(ss_bin=args.ss_bin, print_ss_log=args.print_ss_log)

    yassp = YaSSP('http://localhost:8000/', 'Localhost', 'TEST123')
    print(yassp.get_all_profiles())
    return

    try:
        manager.start()
        
        manager.update(servers)
        manager._stat_thread.join()
    except KeyboardInterrupt:
        logging.info('Stopped by ^C.')
    finally:
        manager.stop()


if __name__ == '__main__':
    main()

