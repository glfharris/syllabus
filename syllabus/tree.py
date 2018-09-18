from aqt.qt import *

from PyQt5.QtWidgets import QTreeView

from .info import getTags, getParent, getSkel, isChild, getDecks, getHiers
from .node import Node
from .stats import note_count

class SyllabusTreeView(QTreeView):

    NAME, COUNT, PC = range(3)

    def __init__(self):
        super().__init__()
        self.model = QStandardItemModel(0,2)

        self.model.setHeaderData(0, Qt.Horizontal, 'Name')
        self.model.setHeaderData(1, Qt.Horizontal, 'Count')
        self.model.setHeaderData(2, Qt.Horizontal, 'Percent %')

        self.setModel(self.model)
        
        tree = Node('collection', 'collection', 'collection')
        print(tree.name)
        tree.acquire_child_decks()
        tree.acquire_child_tags()
        print(tree.children)

        self._populateTree([tree], self.model.invisibleRootItem())
    
    def _populateTree(self, children, parent):
        for child in children:
            row = child.to_row()
            parent.appendRow(row)

            self._populateTree(child.children, row[0])

    
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


def genDecks():
    decks = list(getDecks().values())


