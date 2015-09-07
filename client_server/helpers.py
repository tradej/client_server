
from devassistant import bin, actions

def get_runnables():
    '''Get a list of runnable assistants and actions'''
    top = bin.TopAssistant()
    tree = top.get_subassistant_tree() + tuple(actions.actions)
    names = get_names(tree)
    return names

def get_names(item):
    '''Get names of subassistants and subactions'''
    return {item[0].name: [get_names(a) for a in item[1]]}
