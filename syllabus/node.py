from aqt import mw

from .info import *

class Node:
    def __init__(self, name, kind, deck):
        self.deck = deck
        self.name = name
        self.kind = kind
        self.children = []

def getAppleJuice():
    decks = list(set(getDecks().values()))
    deck_lookup = {v: k for k, v in getDecks().items()}

    res = []

    
