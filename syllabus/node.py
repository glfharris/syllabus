import sys

from aqt import mw, qt

from .info import *
from .stats import *

sys.setrecursionlimit(4000)

class Node:
    tag_names = {}
    def __init__(self, name, kind, deck):
        self.deck = deck
        self.name = name
        self.kind = kind
        self.children = []
    
    def __repr__(self):
        return '<{} - {}>'.format(self.kind, self.name)
    
    def to_row(self):
        name = qt.QStandardItem(self.name)
        count = qt.QStandardItem(str(self.acquire_count()))
        return [name, count]

    
    def acquire_count(self, tot=0):
        if self.kind is 'deck':
            return note_count(self.deck)
        if self.kind is 'tag':
            return note_count(self.deck, tag=self.name)
        if self.kind is 'collection':
            return mw.col.db.scalar('select count() from cards')

    def acquire_child_tags(self):
        if self.deck not in self.tag_names.keys():
            self.tag_names[self.deck] = tags_by_deck(self.deck)

        for tag_name in self.tag_names[self.deck]:
            tag = Node(tag_name, 'tag', self.deck)
            if self.kind is 'deck' and tag.is_child() is False:
                self.children.append(tag)
            elif self.kind is 'tag' and self.is_parent_of(tag):
                self.children.append(tag)
        
        for child in self.children:
            child.acquire_child_tags()

    def acquire_child_decks(self):
        if self.kind is 'deck' or 'collection':
            decks = getDecks()

            for k, v in decks.items():
                node = Node(v, 'deck', k)
                if self.is_parent_of(node):
                    self.children.append(node)
            
            for child in self.children:
                child.acquire_child_decks()

    def is_parent_of(self, node):
        if self.name == node.gen_parent_name():
            return True
        elif self.kind == 'collection' and node.is_child() == False:
            return True
        else:
            return False
    
    def is_child_of(self, node):
        pass
    
    def gen_parent_name(self):
        parts = self.name.split('::')
        if len(parts) < 2:
            return None
        else:
            return '::'.join(parts[:-1])
    
    def is_child(self):
        parts = self.name.split('::')
        if len(parts) < 2:
            return False
        else:
            return True
    
    def change_deck(deck):
        self.deck = deck
        for child in self.children:
            child.change_deck(deck)

def generate_tag_tree():
    tags = getHiers('tags')
    tree = []

    for tag in tags:
        tag_node = Node(tag, 'tag', '')
        if tag_node.is_child() is False:
            tree.append(tag_node)
