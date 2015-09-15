import asyncio
import json

from devassistant.command_helpers import DialogHelper


@DialogHelper.register_helper
class JSONDialogHelper(object):
    shortname = 'json'
    yes_list = ['y', 'yes']
    yesno_list = yes_list + ['n', 'no']

    @classmethod
    def is_available(cls):
        return True

    @classmethod
    def is_graphical(cls):
        return False

    @classmethod
    @asyncio.coroutine
    def ask_for_confirm_with_message(cls, prompt, message, **options):
        prompt += ' [y/n]'
        while True:
            choice = ask_for_input_with_prompt(cls, prompt, message, **options)
            choice = choice.lower()
            if choice not in cls.yesno_list:
                options['__handler__'].send_error('You have to choose one of y/n.')
            else:
                return choice in cls.yes_list

    @classmethod
    @asyncio.coroutine
    def ask_for_package_list_confirm(cls, prompt, package_list, **options):
        prompt += ' [y(es)/n(o)/s(how)]: '
        while True:
            choice = ask_for_input_with_prompt(cls, prompt, **options)
            choice = choice.lower()
            if choice not in cls.yesno_list + ['s', 'show']:
                options['__handler__'].send_error('You have to choose one of y/n/s.')
            else:
                if choice in cls.yesno_list:
                    return choice in cls.yes_list
                else:
                    print('\n'.join(sorted(package_list)))
                    # TODO log this instead of printing

    @classmethod
    @asyncio.coroutine
    def _ask_for_text_or_password(cls, prompt, type, **options):
        print('bulsity')
        question = {'id': options['__id__'], 'promt': promt, 'type': type}
        msg = options.get('message', None)
        if msg:
            question['message'] = msg
        options['__handler__'].send_message({'question': question})

        while True:
            try:
                reply = options['__handler__'].get_answer()
                if reply['answer']['id'] != options['__id__']:
                    raise(Exception('Invalid id'))
                inp = reply['answer']['value']
                return inp
            except BaseException as e:
                options['__handler__'].send_error(e)

    @classmethod
    @asyncio.coroutine
    def ask_for_input_with_prompt(cls, prompt, **options):
        return _ask_for_text_or_password(cls, prompt, 'input_with_prompt', **options)

    @classmethod
    @asyncio.coroutine
    def ask_for_password(cls, prompt, **options):
        return _ask_for_text_or_password(cls, prompt, 'password', **options)
