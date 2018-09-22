import os
import sys

from aqt import mw, qt

from .info import tags_by_deck, getDecks
from .stats import *

# The Order for these must remain the same otherwise shenanigans
HEADER_LABELS = ['Name', 'Kind', 'Deck', 'Total', 'New', 'Learning', 'Young', 'Mature', 'Buried', 'Suspended']
NAME,KIND, DECK, TOTAL,NEW,LEARNING,YOUNG,MATURE,BURIED,SUSPENDED= range(len(HEADER_LABELS))
DEFAULT_COLUMNS = [NAME, TOTAL, NEW, LEARNING, YOUNG, MATURE]

# sys.setrecursionlimit(4000)

class Node:
    tag_names = {}
    def __init__(self, name, kind, deck):
        self.deck = deck
        self.name = name
        self.kind = kind
        self.children = []
        self.data = {}
    
    def __repr__(self):
        return '<{} - {}>'.format(self.kind, self.name)

# Data methods
    def card_total(self):
        if 'total' not in self.data.keys():
            if self.kind is 'tag':
                self.data['total'] = count_total(deck=self.deck, tag=self.name)
            elif self.kind is 'deck':
                tmp = count_total(deck=self.deck)
                for child in self.children:
                    if child.kind is 'deck':
                        tmp += child.card_total()
                self.data['total'] = tmp
            else:
                self.data['total'] = count_total(deck=self.deck)
        return self.data['total']
    
    def card_new(self):
        if 'new' not in self.data.keys():
            if self.kind is 'tag':
                self.data['new'] = count_new(deck=self.deck, tag=self.name)
            elif self.kind is 'deck':
                tmp = count_new(deck=self.deck)
                for child in self.children:
                    if child.kind is 'deck':
                        tmp += child.card_new()
                self.data['new'] = tmp
            else:
                self.data['new'] = count_new(deck=self.deck)
        return self.data['new']
    
    def card_learning(self):
        if 'learning' not in self.data.keys():
            if self.kind is 'tag':
                self.data['learning'] = count_learning(deck=self.deck, tag=self.name)
            elif self.kind is 'deck':
                tmp = count_learning(deck=self.deck)
                for child in self.children:
                    if child.kind is 'deck':
                        tmp += child.card_learning()
                self.data['learning'] = tmp
            else:
                self.data['learning'] = count_learning(deck=self.deck)
        return self.data['learning']
    
    def card_young(self):
        if 'young' not in self.data.keys():
            if self.kind is 'tag':
                self.data['young'] = count_young(deck=self.deck, tag=self.name)
            elif self.kind is 'deck':
                tmp = count_young(deck=self.deck)
                for child in self.children:
                    if child.kind is 'deck':
                        tmp += child.card_young()
                self.data['young'] = tmp
            else:
                self.data['young'] = count_young(deck=self.deck)
        return self.data['young']
    
    def card_mature(self):
        if 'mature' not in self.data.keys():
            if self.kind is 'tag':
                self.data['mature'] = count_mature(deck=self.deck, tag=self.name)
            elif self.kind is 'deck':
                tmp = count_mature(deck=self.deck)
                for child in self.children:
                    if child.kind is 'deck':
                        tmp += child.card_mature()
                self.data['mature'] = tmp
            else:
                self.data['mature'] = count_mature(deck=self.deck)
        return self.data['mature']
    
    def card_suspended(self):
        if 'suspended' not in self.data.keys():
            if self.kind is 'tag':
                self.data['suspended'] = count_suspended(deck=self.deck, tag=self.name)
            elif self.kind is 'deck':
                tmp = count_suspended(deck=self.deck)
                for child in self.children:
                    if child.kind is 'deck':
                        tmp += child.card_suspended()
                self.data['suspended'] = tmp
            else:
                self.data['suspended'] = count_suspended(deck=self.deck)
        return self.data['suspended']
    
    def card_buried(self):
        if 'buried' not in self.data.keys():
            if self.kind is 'tag':
                self.data['buried'] = count_buried(deck=self.deck, tag=self.name)
            elif self.kind is 'deck':
                tmp = count_buried(deck=self.deck)
                for child in self.children:
                    if child.kind is 'deck':
                        tmp += child.card_buried()
                self.data['buried'] = tmp
            else:
                self.data['buried'] = count_buried(deck=self.deck)
        return self.data['buried']
            

# QObject Output Methods
    
    def to_row(self, cols=[0]):
        res = []
        name = qt.QStandardItem(self.name) # We need NAME regardless of whether in cols
        name.setIcon(qt.QIcon(':/icons/{}.svg'.format(self.kind)))
        res.append(name)

        res.append(qt.QStandardItem(self.kind))
        res.append(qt.QStandardItem(self.deck))

        if TOTAL in cols:
            res.append(self.q_total())
        else:
            res.append(qt.QStandardItem())
        
        if NEW in cols:
            res.append(self.q_new())
        else:
            res.append(qt.QStandardItem())
        
        if LEARNING in cols:
            res.append(self.q_learning())
        else:
            res.append(qt.QStandardItem())

        if YOUNG in cols:
            res.append(self.q_young())
        else:
            res.append(qt.QStandardItem())
        
        if MATURE in cols:
            res.append(self.q_mature())
        else:
            res.append(qt.QStandardItem())
        
        if BURIED in cols:
            res.append(self.q_buried())
        else:
            res.append(qt.QStandardItem())
        
        if SUSPENDED in cols:
            res.append(self.q_suspended())
        else:
            res.append(qt.QStandardItem())
        
        return res


    def q_total(self):
        q_total = qt.QStandardItem(str(self.card_total()))

        return q_total
    
    def q_new(self):
        q_new = qt.QStandardItem(str(self.card_new()))
        q_new.setForeground(qt.QColor(0,0,255))

        return q_new
    
    def q_learning(self):
        q_learning = qt.QStandardItem(str(self.card_learning()))
        q_learning.setForeground(qt.QColor(221, 17, 0))

        return q_learning
    
    def q_young(self):
        q_young = qt.QStandardItem(str(self.card_young()))
        q_young.setForeground(qt.QColor(119, 204, 119))

        return q_young
    
    def q_mature(self):
        q_mature = qt.QStandardItem(str(self.card_mature()))
        q_mature.setForeground(qt.QColor(0, 119, 0))

        return q_mature
    
    def q_buried(self):
        q_buried = qt.QStandardItem(str(self.card_buried()))

        return q_buried

    def q_suspended(self):
        q_suspended = qt.QStandardItem(str(self.card_suspended()))

        return q_suspended
# File Output Methods

    def collate_dicts(self, res=[]):
        tmp = {'name': self.name, 'deck': self.deck, 'kind': self.kind}
        for k,v in self.data.items():
            tmp[k] = v
        res.append(tmp)
        for child in self.children:
            child.collate_dicts(res)
        return res
    
# Tree Construction Methods

    def acquire_child_tags(self):
        if self.deck not in self.tag_names.keys():
            self.tag_names[self.deck] = tags_by_deck(self.deck)
        tmp = []
        for tag_name in self.tag_names[self.deck]:
            tag = Node(tag_name, 'tag', self.deck)
            if self.kind is 'deck' and tag.is_child() is False:
                tmp.append(tag)
            elif self.kind is 'tag' and self.is_parent_of(tag):
                tmp.append(tag)
        tmp.sort(key=lambda x: x.name, reverse=True)
        self.children += tmp
        for child in self.children:
            child.acquire_child_tags()

    def acquire_child_decks(self):
        if self.kind is 'deck' or 'collection':
            decks = getDecks()
            tmp = []
            for k, v in decks.items():
                node = Node(v, 'deck', k)
                if self.is_parent_of(node):
                    tmp.append(node)
            tmp.sort(key=lambda x: x.name, reverse=True)
            self.children += tmp
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
