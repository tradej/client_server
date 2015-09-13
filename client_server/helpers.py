from six import string_types

from devassistant import actions

from client_server import exceptions

def get_tree(depth, icons, root):
    tree = get_all_actions(depth, icons, root, prefix=root + '/')
    return {'tree': tree}

def get_detail(*args, **kwargs):
    raise exceptions.ProcessingError('Not Implemented')

def run_runnable(*args, **kwargs):
    raise exceptions.ProcessingError('Not Implemented')


def get_all_actions(depth, icons, root, currentdepth=1, prefix=''):
    tree = []
    root = get_root(root)

    for action in root:
        if action.hidden:
            continue

        a = {
            'name': action.name,
            'fullname': action.name,
            'description': action.description,
            'path': prefix + action.name,
            'icon': None,  # actions currently have no icons
        }

        if not depth or depth > currentdepth:
            a['children'] = get_all_actions(depth, icons, root=action,
                                            currentdepth=currentdepth+1,
                                            prefix=a['path'] + '/')

        tree.append(a)
    return tree


def get_root(root):
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
