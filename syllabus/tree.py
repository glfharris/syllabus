from aqt.qt import *

from PyQt5.QtWidgets import QTreeView

from .info import getParent, isChild, getDecks, getHiers
from .node import Node

header_labels = ['Name', 'Total', 'New', 'Learning', 'Young', 'Mature']

class SyllabusTreeView(QTreeView):

    def __init__(self):
        super().__init__()
        
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(header_labels)
        self.setModel(self.model) 
        
        tree = Node('collection', 'collection', 'collection')
        tree.acquire_child_decks()
        tree.acquire_child_tags()

        self._populateTree([tree], self.model.invisibleRootItem())

        self.expandAll()
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        for i in range(len(header_labels)):
            self.resizeColumnToContents(i)
    
    def _populateTree(self, children, parent):
        for child in children:
            row = child.to_row()
            parent.appendRow(row)
            self._populateTree(child.children, row[0])


