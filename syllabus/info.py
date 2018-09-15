from aqt import mw

from .stats import note_count

class DataTree:
    def __init__(self):
        self.tree = getTree()
        self.populate_tree()

    def populate_tree(self):

        for id in self.tree.keys():
            for tag in self.tree[id]['tags'].keys():
                self.tree[id]['tags'][tag]['count'] = note_count(id, tag = tag)

def getDecks():
    decks = {}
    for k,v in mw.col.decks.decks.items():
        decks[k] = v['name']
    return decks

def getTags(deck):
    return mw.col.tags.byDeck(deck)

def getTree():
    tree = {}
    decks = getDecks()

    for id, name in decks.items():
        tags = getTags(id)
        tree[id] =  {'id': id, 'name': name, 'tags': {}, 'stats':{}}
        for tag in tags:
            tree[id]['tags'][tag] = {}
    return tree

def getSkel():
    skel = {}
    tmp = {}
    decks = getDecks()

    for id, name in decks.items():
        tags = getTags(id)
        tmp[name] = tags
    
    for name, tags in tmp.items():
        if isChild(name):
            parent = getParent(name)
            skel[parent]
        else:
            skel[name] = tags

    return skel
    
    

def getParent(name):
    parts = name.split('::')
    if len(parts) < 2:
        return None
    else:
        return '::'.join(parts[:-1])

def isChild(name):
    if len(name.split('::')) > 1:
        return True
    else:
        return False

def getHier(name):
    res = []
    parts = name.split('::')

    for x in range(len(parts)):
        res.append('::'.join(parts[:(x+1)]))
    return res

def getHiers(kind):
    if kind == 'decks':
        names = list(getDecks().values())
    elif kind == 'tags':
        names = mw.col.tags.tags.keys()
    tmp = []
    for deck in names:
        tmp += getHier(deck)
    return list(set(tmp))
