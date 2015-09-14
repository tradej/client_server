
import os
import asyncio

from client_server import handlers, settings
from client_server.logger import logger

class UnixServer(object):

    def __init__(self, filename=settings.SOCKET_FILENAME):
        self.filename = filename

    def start(self):
        self._prep_socket()
        loop = asyncio.get_event_loop()
        startup = asyncio.start_unix_server(self._accept_client, path=self.filename, backlog=0)
        loop.run_until_complete(startup)
        logger.info('Listening on {fn}'.format(fn=self.filename))
        loop.run_forever()

    def _prep_socket(self):
        try:
            os.unlink(self.filename)
        except OSError:
            pass

    @asyncio.coroutine
    def _accept_client(self, reader, writer):
        logger.info('Received connection')
        try:
            while True: # Listening for all incoming messages
                data = yield from asyncio.wait_for(reader.readline(), timeout=None)
                if not data:
                    break
                else:
                    yield from handlers.RequestHandler(reader, writer).handle(data)

        except Exception as e:
            logger.error('Unexpected exception: ' + str(e))
            writer.write('Server error\n'.encode('utf-8'))
            raise(e)

        finally:
            logger.info('Connection closed')
