import aqt
from aqt import mw
from aqt.qt import QAction
from aqt.utils import qconnect

from .dialog import SyllabusDialog

DIALOG_NAME = "Syllabus"


def syllabus_launcher():
    aqt.dialogs.open(DIALOG_NAME, mw)


aqt.dialogs.register_dialog(DIALOG_NAME, SyllabusDialog)

action = QAction("Syllabus", mw)
qconnect(action.triggered, syllabus_launcher)

mw.form.menuTools.addAction(action)
