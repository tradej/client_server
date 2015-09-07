
import os
import logging
import asyncio

from client_server import exceptions, handlers, settings

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

class UnixServer(object):

    def __init__(self, filename=settings.SOCKET_FILENAME):
        self.filename = filename

    def start(self):
        self._prep_socket()
        loop = asyncio.get_event_loop()
        startup = asyncio.start_unix_server(self._accept_client, path=self.filename, backlog=0)
        loop.run_until_complete(startup)
        logger.info('Listening on {fn}'.format(fn=self.filename))
        try:
            loop.run_forever()
        finally:
            loop.close()

    def _prep_socket(self):
        try:
            os.unlink(self.filename)
        except OSError:
            pass

    def _accept_client(self, reader, writer):
        logger.info('Received connection')
        task = asyncio.Task(self._handle_client(reader, writer))

    @asyncio.coroutine
    def _handle_client(self, reader, writer):
        while True:
            data = yield from asyncio.wait_for(reader.readline(), timeout=None)
            reply = handlers.RequestHandler.handle(data)
            writer.write(reply)
            if not data or data.decode().rstrip() == 'BYE':
                logger.info('Connection closed')
                break

