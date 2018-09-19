import os
import sys

from aqt import mw, qt

from .info import tags_by_deck, getDecks
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
        if self.kind is 'deck':
            name.setIcon(qt.QIcon('/home/glfharris/src/syllabus/syllabus/icons/deck.svg'))
        if self.kind is 'tag':
            name.setIcon(qt.QIcon('/home/glfharris/src/syllabus/syllabus/icons/tag.svg'))
        if self.kind is 'collection':
            name.setIcon(qt.QIcon('/home/glfharris/src/syllabus/syllabus/icons/collection.svg'))

        return [name, self.q_total(), self.q_new(), self.q_learning(), self.q_young(), self.q_mature()]


    def q_total(self):
        if self.kind is 'tag':
            count = count_total(deck=self.deck, tag=self.name)
        else:
            count = count_total(deck=self.deck)
        
        q_total = qt.QStandardItem(str(count))

        return q_total
    
    def q_new(self):
        if self.kind is 'tag':
            count = count_new(deck=self.deck, tag=self.name)
        else:
            count = count_new(deck=self.deck)
        
        q_new = qt.QStandardItem(str(count))
        q_new.setForeground(qt.QColor(0,0,255))

        return q_new
    
    def q_learning(self):
        if self.kind is 'tag':
            count = count_learning(deck=self.deck, tag=self.name)
        else:
            count = count_learning(deck=self.deck)
        
        q_learning = qt.QStandardItem(str(count))
        q_learning.setForeground(qt.QColor(221, 17, 0))
        return q_learning
    
    def q_young(self):
        if self.kind is 'tag':
            count = count_young(deck=self.deck, tag=self.name)
        else:
            count = count_young(deck=self.deck)
        
        q_young = qt.QStandardItem(str(count))
        q_young.setForeground(qt.QColor(119, 204, 119))

        return q_young
    
    def q_mature(self):
        if self.kind is 'tag':
            count = count_mature(deck=self.deck, tag=self.name)
        else:
            count = count_mature(deck=self.deck)
        
        q_mature = qt.QStandardItem(str(count))
        q_mature.setForeground(qt.QColor(0, 119, 0))

        return q_mature

    
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
