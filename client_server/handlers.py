
from client_server import helpers

class RequestHandler(object):

    @classmethod
    def handle(cls, data):
        sanitized_data = data.decode().strip()
        return (cls.process(sanitized_data) + '\n').encode()

    @classmethod
    def process(cls, data):
        if data == 'QUERY':
            return 'OK'
        if data.startswith('INFO'):
            return 'OK'
        if data == 'BYE':
            return 'BYE'
        else:
            return 'ERR invalid'

