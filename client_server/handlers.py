
import asyncore
import time

from client_server import helpers

class ServerHandler(asyncore.dispatcher_with_send):

    def handle_read(self):
        data = self.recv(8192)
        self.send(self._format_reply(data))

    def _format_reply(self, data):
        clean_data = data.decode('utf-8').replace('\n', '')
        return (self._process(clean_data) + '\n').encode('utf-8')

    def _process(self, data):
        if data.startswith('QUERY'):
            return 'OK ' + str(helpers.get_runnables())
        else:
            return 'ERR no such call: ' + data
