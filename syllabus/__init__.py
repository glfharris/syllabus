import aqt
from aqt import mw, DialogManager
from aqt.qt import *
from aqt.utils import showInfo

from .syllabus import Syllabus

DialogManager._dialogs["Syllabus"] = [Syllabus, None]

def syllabusLauncher():
    aqt.dialogs.open("Syllabus", mw)

a = QAction("Syllabus", mw)
a.triggered.connect(syllabusLauncher)

mw.form.menuTools.addAction(a)

