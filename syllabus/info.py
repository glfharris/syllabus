from aqt import mw

def getDecks():
    decks = {}
    for k,v in mw.col.decks.decks.items():
        decks[k] = v['name']
    return decks

def tags_by_deck(deck):
    tmp = []
    names =  mw.col.tags.byDeck(deck)
    for tag in names:
        tmp += getHier(tag)
    return list(set(tmp))

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
