import os
import sys

from aqt import mw, qt

from .info import tags_by_deck, getDecks
from .stats import *

# The Order for these must remain the same otherwise shenanigans
HEADER_LABELS = ['Name', 'Kind', 'Deck', 'Total', 'New', 'Learning', 'Young', 'Mature', 'Buried', 'Suspended', 'Ease', 'Young Retention', 'Mature Retention', 'Total Retention' ]
NAME,KIND, DECK, TOTAL,NEW,LEARNING,YOUNG,MATURE,BURIED,SUSPENDED,EASE,YOU_RENT, MAT_RENT, TOT_RENT = range(len(HEADER_LABELS))
DEFAULT_COLUMNS = [NAME, TOTAL, NEW, LEARNING, YOUNG, MATURE]

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
    def _query(self, func, val, **kwargs): # func is the function from .stats to us, val is the self.data key to story computed value
        if val not in self.data.keys():
            if self.kind is 'tag':
                res = func(deck=[self.deck], tag=self.name, **kwargs)
            elif self.kind is 'deck':
                decks = [self.deck] + self.get_child_dids(res=[])
                res = func(deck=decks, **kwargs)
            else:
                res = func(**kwargs)
            self.data[val] = res
        return self.data[val]

    def card_total(self):
        return self._query(total, 'total')
    
    def card_new(self):
        return self._query(new, 'new')
    
    def card_learning(self):
        return self._query(learning, 'learning')
    
    def card_young(self):
        return self._query(young, 'young')
    
    def card_mature(self):
        return self._query(mature, 'mature')
    
    def card_suspended(self):
        return self._query(suspended, 'suspended')
    
    def card_buried(self):
        return self._query(buried, 'buried')
    
    def card_ease(self):
        return self._query(ease, 'ease')
    
    def rev_mature_retention(self):
        return self._query(retention, 'mature_retention', retention='mature')
    
    def rev_young_retention(self):
        return self._query(retention, 'young_retention', retention='young')
    
    def rev_total_retention(self):
        return self._query(retention, 'total_retention', retention='total') # retention=total is a bit sloppy, not actually handled
            

# QObject Output Methods
    
    def to_q_row(self, cols=[0]):
        func_dict = {NAME: self.q_name, KIND: self.q_kind, DECK: self.q_deck, TOTAL: self.q_total, NEW: self.q_new, LEARNING: self.q_learning,
                     YOUNG: self.q_young, MATURE: self.q_mature, BURIED: self.q_buried, SUSPENDED: self.q_suspended, EASE: self.q_ease,
                     YOU_RENT: self.q_young_retention, MAT_RENT: self.q_mature_retention, TOT_RENT: self.q_total_retention}

        q_row = []
        for x in range(len(HEADER_LABELS)):
            q_row.append(qt.QStandardItem())

        for column in cols:
            q_row[column] = func_dict[column]()
        
        return q_row

    def q_name(self):
        name = qt.QStandardItem(self.name) # We need NAME regardless of whether in cols
        name.setIcon(qt.QIcon(':/icons/{}.svg'.format(self.kind)))
        return name
    
    def q_kind(self):
        return qt.QStandardItem(self.kind)
    
    def q_deck(self):
        return qt.QStandardItem(self.deck)

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
    
    def q_ease(self):
        tmp = self.card_ease()
        if tmp:
            q_ease = qt.QStandardItem('{:.0%}'.format(self.card_ease() / 1000))
        else:
            q_ease = qt.QStandardItem()

        return q_ease
    
    def q_mature_retention(self):
        try:
            q_mature_retention = qt.QStandardItem('{:.2%}'.format(self.rev_mature_retention()))
        except ZeroDivisionError:
            q_mature_retention = qt.QStandardItem()

        return q_mature_retention
    
    def q_young_retention(self):
        try:
            q_young_retention = qt.QStandardItem('{:.2%}'.format(self.rev_young_retention()))
        except ZeroDivisionError:
            q_young_retention = qt.QStandardItem()

        return q_young_retention
    
    def q_total_retention(self):
        try:
            q_total_retention = qt.QStandardItem('{:.2%}'.format(self.rev_total_retention()))
        except ZeroDivisionError:
            q_total_retention = qt.QStandardItem()

        return q_total_retention
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

    def get_child_dids(self, res=[]):
        if self.kind == 'tag':
            return None
        else:
            for child in self.children:
                if child.kind == 'deck':
                    res.append(child.deck)
                child.get_child_dids(res=res)
        return list(set(res))