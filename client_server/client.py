
import asyncio
import logging

from client_server import settings

class Client(object):

    def __init__(self):
        self.connection = None
        self.filename = settings.SOCKET_FILENAME
        self.logger = logging.getLogger('da_cli_client')


