#!/usr/bin/python3

import argparse
import sys

from client_server import settings
from client_server.server import UnixServer

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='DA Server Prototype')
    ap.add_argument('type', choices=['unix', 'inet'])
    args = vars(ap.parse_args())

    try:
        if args['type'] == 'unix':
            server = UnixServer(settings.SOCKET_FILENAME)
        elif args['type'] == 'inet':
            print('Inet socket not implemented yet')
            sys.exit(1)
        server.start()
    except KeyboardInterrupt:
        print('Killed by user')

