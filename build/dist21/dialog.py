import aqt
from aqt.qt import *

from .deck import getDecks
from .stats import note_count
from .ui_dialog import Ui_Syllabus

class SyllabusDialog(QDialog, Ui_Syllabus):

    def __init__(self, mw):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.mw = mw

        self.populate_combo()
        self.deckCombo.currentIndexChanged.connect(self.deck_changed)

        self.curr_deck = str(self.mw.col.decks.active())
        self.refresh_list()

        self.show()
        self.activateWindow()

    def populate_combo(self):
        decks = getDecks()
        for k,v in decks.items():
            self.deckCombo.addItem(v,k)

    def deck_changed(self, i):
        self.curr_deck = self.deckCombo.itemData(i)
        self.refresh_list()

    def refresh_list(self):
        self.tagList.clear()

        tags = self.mw.col.tags.byDeck(self.curr_deck)
        tags.sort()
        total = note_count(self.curr_deck)
        if total > 0:
            self.tagList.addItem("{}\t{:.0%}\tAll".format(total, total/total))

        if tags:
            for tag in tags:
                tag_count = note_count(self.curr_deck, tag=tag)
                self.tagList.addItem("{}\t{:.0%}\t{}".format(tag_count, (tag_count/total), tag))

    def reject(self):
        aqt.dialogs.markClosed("Syllabus")
        QDialog.reject(self)
    
    def closeWithCallback(self, callback):
        self.reject()
        callback()
