from aqt.qt import *

from PyQt5.QtWidgets import QTreeView

from .info import getTags, getParent, getSkel, isChild, getDecks, getHiers
from .stats import note_count

class SyllabusTreeView(QTreeView):

    NAME, COUNT, PC = range(3)

    def __init__(self):
        super().__init__()
        self.model = QStandardItemModel()

        self.model.setHeaderData(self.NAME, Qt.Horizontal, 'Name')
        self.model.setHeaderData(self.COUNT, Qt.Horizontal, 'Count')
        self.model.setHeaderData(self.PC, Qt.Horizontal, 'Percent %')

        self.setModel(self.model)
        print(getHiers('tags'))

        data = getSkel()

        self._populateTree(data, self.model.invisibleRootItem())
    
    def _populateTree(self, children, parent):
        for child in sorted(children):
            child_item = QStandardItem(child)
            parent.appendRow(child_item)
            if isinstance(children, type({})):
                self._populateTree(children[child], child_item)
    
    def deck_tree(self, deck):
        model = self.createDataModel()
        self.setModel(model)

        total = note_count(deck)
        tags = getTags(deck)
        tags.sort(reverse=True)

        for tag in tags:
            if tag:
                count = note_count(deck, tag=tag)
                self.addData(model, tag, count, '{:.0%}'.format(count/total))
        

    def createDataModel(self):
        model = QStandardItemModel(0,3,self)
        model.setHeaderData(self.TAG, Qt.Horizontal, 'Tag')
        model.setHeaderData(self.COUNT, Qt.Horizontal, 'Count')
        model.setHeaderData(self.PC, Qt.Horizontal, 'Percent %')
        return model

    def addData(self, model, tag, count, pc):
        model.insertRow(0)
        model.setData(model.index(0, self.TAG), tag)
        model.setData(model.index(0, self.COUNT), count)
        model.setData(model.index(0, self.PC), pc)

class Node:
    def __init__(self, name, kind):
        self.name = name
        self.type = kind
        self.children = []

def genDecks():
    decks = list(getDecks().values())


