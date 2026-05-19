import csv

import aqt
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo

from .columns import (
    COLUMN_SETTINGS,
    DEFAULT_COLUMNS,
    NAME,
)
from .export import collate_tree
from .tree import SyllabusTreeView

ADDON_PACKAGE = __package__.split(".")[0] if __package__ else __name__.split(".")[0]
USER_ROLE = Qt.ItemDataRole.UserRole
CHECKED = Qt.CheckState.Checked
NO_EDIT_TRIGGERS = QAbstractItemView.EditTrigger.NoEditTriggers
HORIZONTAL = Qt.Orientation.Horizontal

DEFAULT_CONFIG = {
    "last_columns": DEFAULT_COLUMNS,
    "show_columns": True,
    "window_size": [980, 620],
    "splitter_sizes": [760, 220],
    "hide_empty": False,
    "show_decks": True,
    "show_tags": False,
    "show_root": True,
    "expanded_nodes": [],
}


def addon_config():
    config = DEFAULT_CONFIG.copy()
    config.update(mw.addonManager.getConfig(ADDON_PACKAGE) or {})
    return config


class SyllabusDialog(QDialog):

    def __init__(self, mw):
        super().__init__(mw)
        self.config = addon_config()
        self.setup_ui()
        self.tree_view = SyllabusTreeView(cols=self.config.get('last_columns', DEFAULT_COLUMNS))

        self.treeLayout.addWidget(self.tree_view)

        self.populate_column_settings()
        self.col_tree.clicked.connect(self.on_tree_view_check)
        self.col_tree.setEditTriggers(NO_EDIT_TRIGGERS)
        
        self.refresh_action.triggered.connect(self.refresh_tree)
        self.export_all_action.triggered.connect(self.export_all)
        self.export_selected_action.triggered.connect(self.export_selected)
        self.export_visible_action.triggered.connect(self.export_visible)
        self.expand_action.triggered.connect(self.tree_view.expand_tree)
        self.collapse_action.triggered.connect(self.tree_view.collapse_tree)
        self.columns_action.toggled.connect(self.toggle_columns_panel)
        self.hide_empty_action.toggled.connect(self.toggle_hide_empty)
        self.show_decks_action.toggled.connect(self.toggle_show_decks)
        self.show_tags_action.toggled.connect(self.toggle_show_tags)
        self.show_root_action.toggled.connect(self.toggle_show_root)
        self.filter_edit.textChanged.connect(self.tree_view.set_filter_text)
        self.apply_col_settings.clicked.connect(self.apply_settings)
        self.tree_view.buildStarted.connect(lambda: self.set_building_state(True))
        self.tree_view.buildFinished.connect(lambda: self.set_building_state(False))
        self.tree_view.exportSubtreeRequested.connect(self.export_subtree)
        self.tree_view.expansionChanged.connect(self.persist_expansion_state)

        self.restore_layout_state()
        self.restore_filter_state()
        self.refresh_tree()
        self.show()
        self.activateWindow()

    def setup_ui(self):
        self.setObjectName("Syllabus")
        self.setWindowTitle("Syllabus")
        self.resize(*self.config.get("window_size", DEFAULT_CONFIG["window_size"]))

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(8, 8, 8, 8)

        self.toolbar = QToolBar(self)
        self.toolbar.setObjectName("toolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.mainLayout.addWidget(self.toolbar)

        self.refresh_action = QAction("Refresh", self)
        self.refresh_action.setToolTip("Rebuild the syllabus tree")
        self.toolbar.addAction(self.refresh_action)

        self.export_all_action = QAction("Export All", self)
        self.export_selected_action = QAction("Export Selected", self)
        self.export_visible_action = QAction("Export Visible", self)

        self.export_menu = QMenu(self)
        self.export_menu.addAction(self.export_all_action)
        self.export_menu.addAction(self.export_selected_action)
        self.export_menu.addAction(self.export_visible_action)

        self.export_button = QToolButton(self)
        self.export_button.setText("Export CSV")
        self.export_button.setToolTip("Export current data to CSV")
        self.export_button.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        self.export_button.setMenu(self.export_menu)
        self.export_button.setDefaultAction(self.export_all_action)
        self.toolbar.addWidget(self.export_button)

        self.toolbar.addSeparator()

        self.expand_action = QAction("Expand", self)
        self.expand_action.setToolTip("Expand all rows")
        self.toolbar.addAction(self.expand_action)

        self.collapse_action = QAction("Collapse", self)
        self.collapse_action.setToolTip("Collapse all rows")
        self.toolbar.addAction(self.collapse_action)

        self.columns_action = QAction("Columns", self)
        self.columns_action.setToolTip("Show or hide column settings")
        self.columns_action.setCheckable(True)
        self.columns_action.setChecked(self.config.get("show_columns", True))
        self.toolbar.addAction(self.columns_action)

        self.hide_empty_action = QAction("Hide Empty", self)
        self.hide_empty_action.setToolTip("Hide rows with no cards")
        self.hide_empty_action.setCheckable(True)
        self.hide_empty_action.setChecked(self.config.get("hide_empty", False))
        self.toolbar.addAction(self.hide_empty_action)

        self.show_decks_action = QAction("Decks", self)
        self.show_decks_action.setCheckable(True)
        self.show_decks_action.setChecked(self.config.get("show_decks", True))
        self.toolbar.addAction(self.show_decks_action)

        self.show_tags_action = QAction("Tags", self)
        self.show_tags_action.setCheckable(True)
        self.show_tags_action.setChecked(self.config.get("show_tags", True))
        self.toolbar.addAction(self.show_tags_action)

        self.show_root_action = QAction("Root", self)
        self.show_root_action.setCheckable(True)
        self.show_root_action.setChecked(self.config.get("show_root", True))
        self.toolbar.addAction(self.show_root_action)

        self.toolbar.addSeparator()

        self.filter_edit = QLineEdit(self)
        self.filter_edit.setObjectName("filter_edit")
        self.filter_edit.setPlaceholderText("Filter decks and tags")
        self.filter_edit.setClearButtonEnabled(True)
        self.filter_edit.setMaximumWidth(320)
        self.toolbar.addWidget(self.filter_edit)

        self.splitter = QSplitter(HORIZONTAL, self)
        self.splitter.setObjectName("splitter")
        self.mainLayout.addWidget(self.splitter)

        self.treeWidget = QWidget(self.splitter)
        self.treeLayout = QVBoxLayout(self.treeWidget)
        self.treeLayout.setObjectName("treeLayout")
        self.treeLayout.setContentsMargins(0, 0, 0, 0)
        self.splitter.addWidget(self.treeWidget)

        self.columnsPanel = QWidget(self.splitter)
        self.columnsPanel.setObjectName("columnsPanel")
        self.columnsLayout = QVBoxLayout(self.columnsPanel)
        self.columnsLayout.setObjectName("columnsLayout")
        self.columnsLayout.setContentsMargins(8, 0, 0, 0)

        self.columns_label = QLabel("Columns", self.columnsPanel)
        self.columns_label.setObjectName("columns_label")
        self.columnsLayout.addWidget(self.columns_label)

        self.col_tree = QTreeView(self.columnsPanel)
        self.col_tree.setObjectName("col_tree")
        self.columnsLayout.addWidget(self.col_tree)

        self.apply_col_settings = QPushButton(self.columnsPanel)
        self.apply_col_settings.setObjectName("apply_col_settings")
        self.apply_col_settings.setToolTip("Apply column selections to tree")
        self.apply_col_settings.setText("Apply Columns")
        self.columnsLayout.addWidget(self.apply_col_settings)

        self.splitter.addWidget(self.columnsPanel)
    
    def populate_column_settings(self):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(['Column'])
        self.column_model = model
        parent_item = model.invisibleRootItem()
        self.col_tree.root = parent_item

        for name, key in COLUMN_SETTINGS:
            tmp = QStandardItem(name)
            tmp.setCheckable(True)

            if isinstance(key, list):
                for child_name, child_key in key:
                    child_tmp = QStandardItem(child_name)
                    child_tmp.setCheckable(True)
                    child_tmp.setData(child_key, USER_ROLE)
                    if child_key in self.config.get('last_columns', DEFAULT_COLUMNS):
                        child_tmp.setCheckState(CHECKED)
                    tmp.appendRow(child_tmp)
            else:
                tmp.setData(key, USER_ROLE)
                if key in self.config.get('last_columns', DEFAULT_COLUMNS):
                    tmp.setCheckState(CHECKED)
            parent_item.appendRow(tmp)
        
        self.col_tree.setModel(model)
        self.col_tree.expandToDepth(1)
        self.col_tree.resizeColumnToContents(0)

    def on_tree_view_check(self, index):
        item_clicked = self.column_model.itemFromIndex(index)

        check_state = item_clicked.checkState()

        for i in range(item_clicked.rowCount()):
            item_clicked.child(i).setCheckState(check_state)
    
    def selected_columns(self):
        def _recur_check(node, res):
            for i in range(node.rowCount()):
                child = node.child(i)
                column = child.data(USER_ROLE)
                if column is not None and child.checkState() == CHECKED:
                    res.append(column)
                else:
                    _recur_check(child, res)
            return res

        return _recur_check(self.col_tree.root, [NAME])

    def refresh_tree(self):
        self.persist_expansion_state()
        self.tree_view.gen_tree(
            cols=self.config.get('last_columns', DEFAULT_COLUMNS),
            build_scope=self.build_scope(),
        )

    def apply_settings(self):
        cols = self.selected_columns()
        self.config['last_columns'] = cols
        self.write_config()
        self.persist_expansion_state()
        self.tree_view.gen_tree(cols=cols, build_scope=self.build_scope())

    def set_building_state(self, building):
        self.refresh_action.setEnabled(not building)
        self.export_button.setEnabled(not building)
        self.expand_action.setEnabled(not building)
        self.collapse_action.setEnabled(not building)
        self.apply_col_settings.setEnabled(not building)
        self.filter_edit.setEnabled(not building)
        if not building:
            self.tree_view.restore_expanded_node_keys(self.config.get("expanded_nodes", []))

    def toggle_columns_panel(self, checked):
        self.columnsPanel.setVisible(checked)
        self.config["show_columns"] = checked
        self.write_config()

    def restore_layout_state(self):
        self.columnsPanel.setVisible(self.config.get("show_columns", True))
        self.splitter.setSizes(self.config.get("splitter_sizes", DEFAULT_CONFIG["splitter_sizes"]))

    def restore_filter_state(self):
        self.tree_view.set_hide_empty(self.config.get("hide_empty", False))

    def toggle_hide_empty(self, checked):
        self.config["hide_empty"] = checked
        self.tree_view.set_hide_empty(checked)
        self.write_config()

    def toggle_show_decks(self, checked):
        self.persist_expansion_state()
        self.config["show_decks"] = checked
        self.write_config()

    def toggle_show_tags(self, checked):
        self.persist_expansion_state()
        self.config["show_tags"] = checked
        self.write_config()

    def toggle_show_root(self, checked):
        self.persist_expansion_state()
        self.config["show_root"] = checked
        self.write_config()

    def build_scope(self):
        return {
            "include_decks": self.config.get("show_decks", True),
            "include_tags": self.config.get("show_tags", True),
            "include_root": self.config.get("show_root", True),
        }

    def write_config(self):
        mw.addonManager.writeConfig(ADDON_PACKAGE, self.config)

    def save_layout_state(self):
        self.persist_expansion_state(write=False)
        self.config["show_columns"] = self.columnsPanel.isVisible()
        self.config["splitter_sizes"] = self.splitter.sizes()
        self.config["window_size"] = [self.size().width(), self.size().height()]
        self.write_config()

    def persist_expansion_state(self, write=True):
        self.config["expanded_nodes"] = self.tree_view.expanded_node_keys()
        if write:
            self.write_config()
    
    def export_all(self):
        if not self.tree_view.tree:
            showInfo("No Syllabus data is available to export.")
            return
        self.output_rows(collate_tree(self.tree_view.tree))

    def export_selected(self):
        node = self.tree_view.selected_node()
        if not node:
            showInfo("Select a row to export.")
            return
        self.export_subtree(node)

    def export_subtree(self, node):
        self.output_rows(collate_tree(node))

    def export_visible(self):
        rows = self.tree_view.visible_export_rows()
        if not rows:
            showInfo("No visible Syllabus data is available to export.")
            return
        self.output_rows(rows)

    def output_rows(self, data):
        path, _ = QFileDialog.getSaveFileName(self,"Export Syllabus Tree","tmp.csv","CSV Files (*.csv)")
        if not path:
            return

        parts = path.split('.')
        if parts[-1] not in ['csv', 'CSV']:
            path += '.csv'

        if not data:
            showInfo("No Syllabus data is available to export.")
            return

        with open(path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

    def reject(self):
        self.save_layout_state()
        aqt.dialogs.markClosed("Syllabus")
        QDialog.reject(self)

    def closeEvent(self, event):
        self.save_layout_state()
        aqt.dialogs.markClosed("Syllabus")
        QDialog.closeEvent(self, event)
    
    def closeWithCallback(self, callback):
        self.reject()
        callback()
