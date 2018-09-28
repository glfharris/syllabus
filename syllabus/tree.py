from aqt import mw
from aqt.qt import *

from PyQt5.QtWidgets import QTreeView

from .info import getParent, isChild, getDecks, getHiers
from .node import Node, HEADER_LABELS, DEFAULT_COLUMNS

class SyllabusTreeView(QTreeView):

    def __init__(self, cols=DEFAULT_COLUMNS):
        super().__init__()
        
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(HEADER_LABELS)
        self.setModel(self.model) 
        
        self.doubleClicked.connect(self.on_double_click)

        
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.gen_tree(cols=cols)
        self.resize(self.sizeHint())
        

    def gen_tree(self, cols=DEFAULT_COLUMNS):
        self.model.removeRows(0, self.model.rowCount())

        mw.progress.start(label='Collecting data and building tree\nThis can take a while for large collections')

        self.tree = Node('collection', 'collection', 'collection')
        self.tree.acquire_child_decks()
        self.tree.acquire_child_tags()


        self._populateTree([self.tree], self.model.invisibleRootItem(), cols=cols)
        self.expandToDepth(1)
        for i in range(len(HEADER_LABELS)):
            self.resizeColumnToContents(i)
            if i not in cols:
                self.hideColumn(i)
            for i in cols:
                self.setColumnHidden(i, False)
        
        mw.progress.finish()
        self.resize(self.viewportSizeHint())
        
    
    def _populateTree(self, children, parent, cols=DEFAULT_COLUMNS):
        for child in children:
            row = child.to_q_row(cols=cols)
            parent.appendRow(row)
            self._populateTree(child.children, row[0], cols=cols)

    def on_double_click(self, node_index):
        #node = self.getData(node_index, 0)
        #browser = aqt.dialogs.open("Browser", mw)
        #browser.form.searchEdit.lineEdit().setText("{}".format(node))
        #browser.onSearchActivated()
        pass