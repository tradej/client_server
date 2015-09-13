
import json

from client_server import helpers, exceptions

class RequestHandler(object):

    @classmethod
    def handle(cls, data):
        try:
            sanitized_data = json.loads(data.decode('utf-8').strip())
            reply = cls.process(sanitized_data)
        except ValueError:
            reply = cls._return_error('Expecting JSON')
        return (json.dumps(reply, sort_keys=True) + '\n').encode()

    @classmethod
    def process(cls, data):
        try:
            kind = list(data.keys())[0].lower()
        except IndexError as e:
            return cls._return_error('Invalid format')

        if kind == 'query':
            return cls._process_query(data)
        elif kind == 'answer':
            return cls._process_answer(data)

    @classmethod
    def _process_query(cls, data):
        params = data['query']
        try:
            # Get the tree of runnables
            if params['request'] == 'tree':
                return helpers.get_tree(depth=params['options'].get('depth', 0),
                                        icons=params['options'].get('icons', 'null'),
                                        root=params['options'].get('root', ''))
            # Get info on a runnable
            elif params['request'] == 'detail':
                return helpers.get_detail(icons=params['options'].get('icons', 'null'),
                                          path=params['options']['path'])
            # Run a runnable with args
            elif params['request'] == 'run':
                return helpers.run_runnable(path=params['options']['path'],
                                            arguments=params['options']['arguments'])
            else:
                raise exceptions.ProcessingError('Invalid request')
        except exceptions.ProcessingError as e:
            return cls._return_error(e)

    @classmethod
    def _process_answer(cls, data):
        raise NotImplementedError

    @classmethod
    def _return_error(cls, error):
        return {'error': {'reason': str(error)}}



