
import uuid
import asyncio
import json

from client_server import helpers, exceptions
from client_server.logger import logger

class RequestHandler(object):

    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer

    @asyncio.coroutine
    def handle(self, raw_data):
        '''Process a message from the client.'''
        try:
            sanitized_data = json.loads(raw_data.decode('utf-8').strip())
            yield from self._process_query(list(sanitized_data.values())[0])
            logger.info('Done.')
        except exceptions.ProcessingError as e:
            logger.info('Processing error: ' + str(e))
            self.send_error(str(e))
        except Exception as e:
            logger.error('Unexpected exception: ' + str(e))
            self.send_error('Invalid request: ' + str(e))

    def _process_query(self, data):
        if data['request'] == 'tree':
            self._send_tree(data['options'])
        elif data['request'] == 'detail':
            self._send_detail(data['options'])
        elif data['request'] == 'run':
            yield from self._run(data['options'])


    def _send_tree(self, options):
        '''Send the tree of runnables'''
        logger.info('Sending tree...')
        self.send_message(helpers.get_tree(depth=options.get('depth', 0),
                          icons=options.get('icons', None),
                          root=options.get('root', ''),
                          arguments=options.get('arguments', False)))

    def _send_detail(self, options):
        '''Send details of the given runnable'''
        logger.info('Sending detail for {path}...'.format(path=options['path']))
        self.send_message(helpers.get_detail(icons=options.get('icons', 'null'),
                                  path=options['path']))

    @asyncio.coroutine
    def _run(self, options):
        if 'path' not in options:
            raise exceptions.ProcessingError('Mission option: path')
        logger.info('Running {path}...'.format(path=options['path']))
        run_id = str(uuid.uuid4()).replace('-', '')
        self.send_message({'run': {'id': run_id}})

        # RUN ASSISTANT HERE

        self.send_message({'finished': {'id': run_id, 'status': 'ok'}})

    @asyncio.coroutine
    def _get_answer(self):
        '''Waits for client's answer and returns it. The calling function must
        be a coroutine as well.

        use it as follows: answer = yield from self._get_answer()
        '''
        data = yield from asyncio.wait_for(self.reader.readline(), timeout=None)
        return json.loads(data.decode('utf-8').strip())

    def send_error(self, error):
        '''Format a DA API-compatible error message from the given string'''
        msg = (json.dumps({'error': {'reason': str(error)}}) + '\n').encode('utf-8')
        self.writer.write(msg)

    def send_message(self, message):
        '''Format a dictionary as a JSON message and send it'''
        msg = (json.dumps(message) + '\n').encode('utf-8')
        self.writer.write(msg)

