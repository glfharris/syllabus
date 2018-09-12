from aqt import mw

def getDecks():
    decks = {}
    for k,v in mw.col.decks.decks.items():
        decks[k] = v['name']
    return decks
