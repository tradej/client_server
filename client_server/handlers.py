
import uuid
import asyncio
import json

from devassistant import actions
from devassistant import bin
from devassistant import exceptions as daexceptions
from devassistant import path_runner
from devassistant.cli import argparse_generator

from client_server import helpers, exceptions, dialog_helper
from client_server import dialog_helper  # import this so it is registered
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
        path = options['path']
        logger.info('Running {path}...'.format(path=path))

        top_assistant = bin.TopAssistant()

        # PROBLEM: parse_args can accept list of arguments (only?)
        # PROBLEM: parse_args calls exit when arguments are invalid (sort of solved)
        # PROBLEM: parse_args displays help  when arguments are invalid
        # PROBLEM: argparse_generator expects assistant/action path as arguments
        # TODO: when solved, move argument processing to helpers

        # We need to get a dictionary with defaults for given assistant
        # and we also need to check if all required arguments are specified
        # this is usually done by argparser itself

        # Doesn't work:
        #tree = top_assistant.get_subassistant_tree()
        #argparser = argparse_generator.ArgparseGenerator.\
        #    generate_argument_parser(tree, actions=actions.actions)
        #try:
        #    args = vars(argparser.parse_args( TODO ))
        #except SystemExit:
        #    raise exceptions.ProcessingError('Invalid arguments')

        run_id = str(uuid.uuid4()).replace('-', '')

        # PROBLEM: sending self in args blows up when something in da tries to deepcopy it
        # Cannot serialize socket object
        # sending function references ends up with the same error
        args = {'__ui__': 'json', '__handler__': self, '__id__': run_id}

        try:
            to_run = helpers.get_action_by_path(path)(**args)
        except exceptions.ProcessingError:
            path = top_assistant.get_selected_subassistant_path(**helpers.path_to_dict(path))
            to_run = path_runner.PathRunner(path, args)

        self.send_message({'run': {'id': run_id}})

        # TODO: send log messages as JSON, don't just display them on server's stdout/err
        try:
            to_run.run()
            self.send_message({'finished': {'id': run_id, 'status': 'ok'}})
        except daexceptions.ExecutionException as e:
            raise exceptions.ProcessingError(str(e))


    @asyncio.coroutine
    def get_answer(self):
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

