import os
import csv

import aqt
from aqt import mw
from aqt.qt import *

from .info import getDecks
from .node import DEFAULT_COLUMNS, HEADER_LABELS
from .tree import SyllabusTreeView
from .ui_dialog import Ui_Syllabus

class SyllabusDialog(QDialog, Ui_Syllabus):

    def __init__(self, mw):
        super().__init__()
        self.setupUi(self)
        self.tree_view = SyllabusTreeView(cols=DEFAULT_COLUMNS)

        self.horizontalLayout.addWidget(self.tree_view, 20)

        self.resize(self.tree_view.viewportSizeHint())

        self.export_btn.clicked.connect(self.output_tree)
        self.apply_col_settings.clicked.connect(self.apply_settings)
        self.populate_column_settings()
        
        

        self.show()
        self.activateWindow()
    
    def populate_column_settings(self):
        for i, label in enumerate(HEADER_LABELS):
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, i)
            if label != 'Name':
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            if i in DEFAULT_COLUMNS and label != 'Name':
                item.setCheckState(Qt.Checked)
            elif label != 'Name':
                item.setCheckState(Qt.Unchecked)
            print(item.data(0), item.data(Qt.UserRole))
            self.col_settings_list.addItem(item)
        self.col_settings_list.setSizeAdjustPolicy(QListWidget.AdjustToContents)
        
        #self.col_settings_list.setMargin(0)
    
    def apply_settings(self):
        res = [0, ]
        for i in range(len(HEADER_LABELS)):
            if self.col_settings_list.item(i).checkState():
                res.append(i)
        self.tree_view.gen_tree(cols=res)
    
    def output_tree(self):
        path, _ = QFileDialog.getSaveFileName(self,"Export Syllabus Tree","tmp.csv","CSV Files (*.csv)")
        parts = path.split('.')
        data = []
        if parts[-1] not in ['csv', 'CSV']:
            path += '.csv'
        if path:
            data = self.tree_view.tree.collate_dicts(res=[]) # Need to instantiate res as [] each time, otherwise remembers

            with open(path, 'w') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)

    def reject(self):
        aqt.dialogs.markClosed("Syllabus")
        QDialog.reject(self)
    
    def closeWithCallback(self, callback):
        self.reject()
        callback()
