import aqt
from aqt.qt import *

from .info import getDecks, getSkel
from .stats import note_count
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

        self.show()
        self.activateWindow()

    def populate_combo(self):
        decks = getDecks()
        for k,v in decks.items():
            self.deck_sel.addItem(v,k)

    def deck_changed(self, i):
        self.curr_deck = self.deck_sel.itemData(i)
        #self.tree_view.deck_tree(self.curr_deck)

    def reject(self):
        aqt.dialogs.markClosed("Syllabus")
        QDialog.reject(self)
    
    def closeWithCallback(self, callback):
        self.reject()
        callback()
