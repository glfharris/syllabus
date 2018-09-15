import aqt
from aqt.qt import *

from .info import getDecks, getTree, DataTree
from .stats import note_count
from .tmp import gen_skel
from .tree import SyllabusTreeView
from .ui_dialog import Ui_Syllabus

class SyllabusDialog(QDialog, Ui_Syllabus):

    TAG, COUNT, PC = range(3)

    def __init__(self, mw):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.tree_view = SyllabusTreeView()
        self.verticalLayout.addWidget(self.tree_view)
        self.mw = mw

        self.populate_combo()
        self.deck_sel.currentIndexChanged.connect(self.deck_changed)

        self.curr_deck = str(self.mw.col.decks.active())

        tmp = gen_skel()
        print(tmp[0])
        print([ x.name for x in tmp[0].children])

        self.show()
        self.activateWindow()

    def populate_combo(self):
        decks = getDecks()
        for k,v in decks.items():
            self.deck_sel.addItem(v,k)

    def deck_changed(self, i):
        self.curr_deck = self.deck_sel.itemData(i)
        #self.tree_view.deck_tree(self.curr_deck)
    
    def setup_tree(self):
        model = self.createDataModel(self)
        self.tree_view.setModel(model)

        total = note_count(self.curr_deck)
        tags = self.mw.col.tags.byDeck(self.curr_deck)
        tags.sort()

        for tag in tags:
            if tag:
                count = note_count(self.curr_deck, tag=tag)
                self.addData(model, tag, count, '{:.0%}'.format(count/total))

        
    
    def createDataModel(self, parent):
        model = QStandardItemModel(0,3,parent)
        model.setHeaderData(self.TAG, Qt.Horizontal, 'Tag')
        model.setHeaderData(self.COUNT, Qt.Horizontal, 'Count')
        model.setHeaderData(self.PC, Qt.Horizontal, 'Percent %')
        return model

    def addData(self, model, tag, count, pc):
        model.insertRow(0)
        model.setData(model.index(0, self.TAG), tag)
        model.setData(model.index(0, self.COUNT), count)
        model.setData(model.index(0, self.PC), pc)

    def reject(self):
        aqt.dialogs.markClosed("Syllabus")
        QDialog.reject(self)
    
    def closeWithCallback(self, callback):
        self.reject()
        callback()
