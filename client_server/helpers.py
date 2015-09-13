from six import string_types

from devassistant import actions
from devassistant import bin

from client_server import exceptions

def get_tree(depth, icons, root, arguments):
    treevalid = True
    tree = []
    try:
        tree = get_actions(depth, icons, root, arguments, prefix=root + '/')
    except exceptions.ProcessingError:
        treevalid = False

    try:
        tree += get_assistants(depth, icons, root, arguments, prefix=root + '/')
    except exceptions.ProcessingError as e:
        if not treevalid:
            raise(e)

    return {'tree': tree}

def get_detail(icons, path):
    prefix = '/'.join(path.split('/')[:-1]) + '/'
    try:
        action = get_action_by_path(path)
        return serialize_action(action, depth=0, icons=icons, arguments=True,
                                currentdepth=0, prefix=prefix, namesonly=True)
    except exceptions.ProcessingError:
        assistant = get_assistant_by_path(path)
        return serialize_assistant(assistant, depth=0, icons=icons, arguments=True,
                                   currentdepth=0, prefix=prefix, namesonly=True)


def run_runnable(*args, **kwargs):
    raise exceptions.ProcessingError('Not Implemented')


def get_actions(depth, icons, root, arguments, currentdepth=1, prefix=''):
    tree = []
    root = get_actions_root(root)

    for action in root:
        if action.hidden:
            continue
        tree.append(serialize_action(action, depth, icons, arguments, currentdepth, prefix))
    return tree


def serialize_action(action, depth, icons, arguments, currentdepth, prefix, namesonly=False):
    a = {
        'name': action.name,
        'fullname': action.name,
        'description': action.description,
        'path': prefix + action.name,
        'icon': None,  # actions currently have no icons
    }

    if arguments:
        a['arguments'] = [a.__dict__ for a in action.args]

    if namesonly:
        a['children'] = [a.name for a in action.get_subactions()]
    elif not depth or depth > currentdepth:
        a['children'] = get_actions(depth, icons, root=action, arguments=arguments,
                                    currentdepth=currentdepth+1,
                                    prefix=a['path'] + '/')
    return a


def get_action_by_path(path):
    segments = path.split('/')
    root = actions.actions
    for segment in segments:
        found = False
        try:
            candidates = root.get_subactions()
        except AttributeError:
            candidates = root
        for candidate in candidates:
            if candidate.name == segment:
                root = candidate
                found = True
                break
        if not found:
            raise exceptions.ProcessingError('Invalid path: ' + path)
    return root


def get_actions_root(root):
    if not root:
        return actions.actions

    if isinstance(root, string_types):
        root = get_action_by_path(root)

    return root.get_subactions()


# TODO get_{assistants,actions}() are almost teh same, unify somehow?

def get_assistants(depth, icons, root, arguments, currentdepth=1, prefix=''):
    tree = []
    root = get_assistants_root(root)

    for assistant in root:
        tree.append(serialize_assistant(assistant, depth, icons, arguments, currentdepth, prefix))
    return tree


def serialize_assistant(assistant, depth, icons, arguments, currentdepth, prefix, namesonly=False):
    a = {
        'name': assistant.name,
        'fullname': assistant.fullname,
        'description': assistant.description,
        'path': prefix + assistant.name,
        'icon': None,  # actions currently have no icons
    }

    if arguments:
        a['arguments'] = [a.__dict__ for a in assistant.args]

    if namesonly:
        a['children'] = [a.name for a in assistant.get_subassistants()]
    elif not depth or depth > currentdepth:
        a['children'] = get_assistants(depth, icons, root=assistant, arguments=arguments,
                                       currentdepth=currentdepth+1,
                                       prefix=a['path'] + '/')
    return a


def get_assistant_by_path(path):
    segments = path.split('/')
    root = bin.TopAssistant()
    for segment in segments:
        found = False
        for candidate in root.get_subassistants():
            if candidate.name == segment:
                root = candidate
                found = True
                break
        if not found:
            raise exceptions.ProcessingError('Invalid path: ' + path)
    return root


def get_assistants_root(root):
    if not root:
        top = bin.TopAssistant()
        return top.get_subassistants()

    if isinstance(root, string_types):
        root = get_assistant_by_path(root)

    return root.get_subassistants()
