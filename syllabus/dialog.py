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

        self.resize(self.tree_view.viewportSizeHint())

        self.show()
        self.activateWindow()

    def reject(self):
        aqt.dialogs.markClosed("Syllabus")
        QDialog.reject(self)
    
    def closeWithCallback(self, callback):
        self.reject()
        callback()
