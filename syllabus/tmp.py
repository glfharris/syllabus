from aqt import mw

class Node:
    def __init__(self, name, kind, id=''):
        self.name = name
        self.id = id
        self.kind = kind
        self.children = []

    def to_dict(self):
        return {'name':name, 'id': id, 'kind': kind, 'children': children}

    def is_child(self):
        if len(self.name.split('::')) > 1:
            return True
        else:
            return False

    def is_child_of(self, query_parent):
        if self.parent_name() == query_parent:
            return True
        else:
            return False

    def parent_name(self):
        if self.is_child():
            parts = self.name.split('::')
            return '::'.join(parts[:-1])
        else:
            return 'collection'

def gen_skel():
    def _populate(lst, res):
        failed = []
        for deck in lst:
            for item in res:
                if deck.is_child_of(item.name):
                    item.children.append(deck)
                else:
                    failed.append(deck)
        # if len(failed) < 1:
        #    return res
        #_populate(failed, res)
        return res

    decks = [x['name'] for x in mw.col.decks.decks.values()]
    tmp = []
    res = [Node('collection', 'collection')]
    for x in decks:
        tmp.append(Node(x, 'deck'))

    res = _populate(tmp, res)
    return res

