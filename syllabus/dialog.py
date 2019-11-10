import os
import csv

import aqt
from aqt import mw
from aqt.qt import *

from .info import getDecks
from .node import *
from .tree import SyllabusTreeView
from .ui_dialog import Ui_Syllabus

config = mw.addonManager.getConfig(__name__)

class SyllabusDialog(QDialog, Ui_Syllabus):

    def __init__(self, mw):
        super().__init__()
        self.setupUi(self)
        self.tree_view = SyllabusTreeView(cols=config['last_columns'])

        self.horizontalLayout.addWidget(self.tree_view, 80)

        self.populate_column_settings()
        self.col_tree.clicked.connect(self.on_tree_view_check)
        self.col_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.export_btn.clicked.connect(self.output_tree)
        self.apply_col_settings.clicked.connect(self.apply_settings)

        self.resize_window()

        self.show()
        self.activateWindow()
    
    def resize_window(self):
        tree_size = self.tree_view.viewportSizeHint()
        group_size = self.groupBox.sizeHint()

        size = QSize(tree_size.width() + group_size.width(), tree_size.height() + 0.5 * group_size.height())
        
        self.resize(size)
    
    def populate_column_settings(self):
        column_dict = {'Total': TOTAL, 'New': NEW, 'Learning': LEARNING, 'Young': YOUNG, 'Mature': MATURE, 'Ease': EASE,
                       'Unqueued': {'Buried': BURIED, 'Suspended': SUSPENDED},
                       'Retention': {'Young Retention': YOU_RENT, 'Mature Retention': MAT_RENT, 'Total Retention': TOT_RENT},
                       'Misc': {'Kind': KIND, 'Deck': DECK}}
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(['Column'])
        self.col_tree.model = model
        parent_item = model.invisibleRootItem()
        self.col_tree.root = parent_item

        for name, key in column_dict.items():
            tmp = QStandardItem(name)
            tmp.setCheckable(True)

            if type(key) == type({}):
                for child_name, child_key in key.items():
                    child_tmp = QStandardItem(child_name)
                    child_tmp.setCheckable(True)
                    child_tmp.setData(child_key, Qt.UserRole)
                    if child_key in config['last_columns']:
                        child_tmp.setCheckState(Qt.Checked)
                    tmp.appendRow(child_tmp)
            else:
                tmp.setData(key, Qt.UserRole)
                if key in config['last_columns']:
                    tmp.setCheckState(Qt.Checked)
            parent_item.appendRow(tmp)
        
        self.col_tree.setModel(model)
        self.col_tree.expandToDepth(1)
        self.col_tree.resizeColumnToContents(0)
        

    def on_tree_view_check(self, index):
        item_clicked = self.col_tree.model.itemFromIndex(index)

        check_state = item_clicked.checkState()

        for i in range(item_clicked.rowCount()):
            item_clicked.child(i).setCheckState(check_state)
        


    
    def apply_settings(self):
        def _recur_check(node, res=[]):
            for i in range(node.rowCount()):
                child = node.child(i)
                if child.data(Qt.UserRole) and child.checkState():
                    res.append(child.data(Qt.UserRole))
                else:
                    _recur_check(child, res=res)
            return res
        
        cols = _recur_check(self.col_tree.root, res=[0])
        self.tree_view.gen_tree(cols=cols)
        self.resize_window()
        config['last_columns'] = cols
        mw.addonManager.writeConfig(__name__, config)
    
    def output_tree(self):
        path, _ = QFileDialog.getSaveFileName(self,"Export Syllabus Tree","tmp.csv","CSV Files (*.csv)")
        parts = path.split('.')
        data = []
        if parts[-1] not in ['csv', 'CSV']:
            path += '.csv'
        if path:
            data = self.tree_view.tree.collate_dicts(res=[]) # Need to instantiate res as [] each time, otherwise remembers

            with open(path, 'w', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)

    def reject(self):
        aqt.dialogs.markClosed("Syllabus")
        QDialog.reject(self)
    
    def closeWithCallback(self, callback):
        self.reject()
        callback()
