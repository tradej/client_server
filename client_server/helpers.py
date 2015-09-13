from six import string_types

from devassistant import actions
from devassistant import bin

from client_server import exceptions

def get_tree(depth, icons, root):
    treevalid = True
    tree = []
    try:
        tree = get_actions(depth, icons, root, prefix=root + '/')
    except exceptions.ProcessingError:
        treevalid = False

    try:
        tree += get_assistants(depth, icons, root, prefix=root + '/')
    except exceptions.ProcessingError as e:
        if not treevalid:
            raise(e)

    return {'tree': tree}

def get_detail(*args, **kwargs):
    raise exceptions.ProcessingError('Not Implemented')

def run_runnable(*args, **kwargs):
    raise exceptions.ProcessingError('Not Implemented')


def get_actions(depth, icons, root, currentdepth=1, prefix=''):
    tree = []
    root = get_actions_root(root)

    for action in root:
        if action.hidden:
            continue

        a = {
            'name': action.name,
            'fullname': action.name,
            'description': action.description,
            'path': prefix + action.name,
            'icon': None,  # actions currently have no icons
            'args': [a.__dict__ for a in action.args],
        }

        if not depth or depth > currentdepth:
            a['children'] = get_actions(depth, icons, root=action,
                                            currentdepth=currentdepth+1,
                                            prefix=a['path'] + '/')

        tree.append(a)
    return tree


def get_actions_root(root):
    if not root:
        return actions.actions

    if isinstance(root, string_types):
        path = root.split('/')
        root = actions.actions
        for segment in path:
            found = False
            for candidate in root:
                if candidate.name == segment:
                    root = candidate
                    found = True
                    break
            if not found:
                raise exceptions.ProcessingError('Invalid root')

    return root.get_subactions()


# TODO get_{assistants,actions}() are almost teh same, unify somehow?

def get_assistants(depth, icons, root, currentdepth=1, prefix=''):
    tree = []
    root = get_assistants_root(root)

    for assistant in root:
        a = {
            'name': assistant.name,
            'fullname': assistant.fullname,
            'description': assistant.description,
            'path': prefix + assistant.name,
            'icon': None,  # actions currently have no icons
            'args': [a.__dict__ for a in assistant.args],
        }

        if not depth or depth > currentdepth:
            a['children'] = get_assistants(depth, icons, root=assistant,
                                           currentdepth=currentdepth+1,
                                           prefix=a['path'] + '/')

        tree.append(a)
    return tree

def get_assistants_root(root):
    if not root:
        top = bin.TopAssistant()
        return top.get_subassistants()

    if isinstance(root, string_types):
        path = root.split('/')
        root = bin.TopAssistant()
        for segment in path:
            found = False
            for candidate in root.get_subassistants():
                if candidate.name == segment:
                    root = candidate
                    found = True
                    break
            if not found:
                raise exceptions.ProcessingError('Invalid root')

    return root.get_subassistants()
