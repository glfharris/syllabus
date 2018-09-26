import aqt
from aqt import mw, DialogManager
from aqt.qt import *
from aqt.utils import showInfo

from .dialog import SyllabusDialog

DialogManager._dialogs["Syllabus"] = [SyllabusDialog, None]

def syllabusLauncher():
    aqt.dialogs.open("Syllabus", mw)

a = QAction("Syllabus", mw)
a.triggered.connect(syllabusLauncher)

mw.form.menuTools.addAction(a)