import aqt
from aqt.qt import *

class Syllabus(QDialog):

    def __init__(self, mw):
        QDialog.__init__(self, mw, Qt.Window)
        mw.setupDialogGC(self)
        self.mw = mw
        self.name = "Syllabus"
        self.silentlyClose = True

        self.setWindowTitle("Syllabus")
        self.setText("This is the Syllabus Dialog")


        self.show()
        self.activateWindow()
    
    def reject(self):
        aqt.dialogs.markClosed("Syllabus")
        QDialog.reject(self)
    
    def closeWithCallback(self, callback):
        self.reject()
        callback()
