import aqt

from aqt import mw
from aqt.qt import *
from aqt.utils import showWarning, tooltip

from .build import build_tree_data
from .columns import (
    COLUMN_BY_ID,
    NAME,
    DEFAULT_COLUMNS,
    HEADER_LABELS,
)
from .export import node_to_row
from .render import NODE_ROLE, SORT_ROLE, node_to_q_row

NO_EDIT_TRIGGERS = QAbstractItemView.EditTrigger.NoEditTriggers
CUSTOM_CONTEXT_MENU = Qt.ContextMenuPolicy.CustomContextMenu


class SyllabusFilterModel(QSortFilterProxyModel):

    def __init__(self):
        super().__init__()
        self.filter_text = ''
        self.hide_empty = False
        self.setSortRole(SORT_ROLE)

    def set_filter_text(self, text):
        self.filter_text = text.strip().lower()
        self.invalidateFilter()

    def set_hide_empty(self, hide_empty):
        self.hide_empty = hide_empty
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        node = self.node_for_source_row(source_row, source_parent)
        if node and not self.accepts_node(node):
            return False

        if not self.filter_text:
            return True

        return self.row_matches_text(source_row, source_parent)

    def row_matches_text(self, source_row, source_parent):
        model = self.sourceModel()
        for column in range(model.columnCount()):
            index = model.index(source_row, column, source_parent)
            value = model.data(index)
            if value and self.filter_text in str(value).lower():
                return True

        parent_index = model.index(source_row, NAME, source_parent)
        for child_row in range(model.rowCount(parent_index)):
            child = self.node_for_source_row(child_row, parent_index)
            if child and not self.accepts_node(child):
                continue
            if self.row_matches_text(child_row, parent_index):
                return True

        return False

    def node_for_source_row(self, source_row, source_parent):
        model = self.sourceModel()
        name_index = model.index(source_row, NAME, source_parent)
        return model.data(name_index, NODE_ROLE)

    def accepts_node(self, node):
        if self.hide_empty and node.total == 0:
            return False
        return True


class SyllabusTreeView(QTreeView):
    buildStarted = pyqtSignal()
    buildFinished = pyqtSignal()
    exportSubtreeRequested = pyqtSignal(object)
    expansionChanged = pyqtSignal()

    def __init__(self, cols=DEFAULT_COLUMNS):
        super().__init__()
        self.tree = None
        self._build_id = 0
        self._structure_template = None
        self._structure_signature = None
        self._current_cols = list(cols)
        self._restoring_expansion = False
        self._build_scope = {
            "include_decks": True,
            "include_tags": True,
            "include_root": True,
        }
        
        self.source_model = QStandardItemModel()
        self.source_model.setHorizontalHeaderLabels(HEADER_LABELS)

        self.proxy_model = SyllabusFilterModel()
        self.proxy_model.setSourceModel(self.source_model)
        self.setModel(self.proxy_model)
        
        self.doubleClicked.connect(self.on_double_click)

        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(NO_EDIT_TRIGGERS)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setUniformRowHeights(True)
        self.setContextMenuPolicy(CUSTOM_CONTEXT_MENU)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.expanded.connect(lambda _: self.emit_expansion_changed())
        self.collapsed.connect(lambda _: self.emit_expansion_changed())
        self.header().setStretchLastSection(False)

        self.resize(self.sizeHint())
        

    def gen_tree(self, cols=DEFAULT_COLUMNS, build_scope=None):
        self._build_id += 1
        build_id = self._build_id
        cols = list(cols)
        self._current_cols = cols
        if build_scope is not None:
            self._build_scope = build_scope

        self.tree = None
        self.source_model.removeRows(0, self.source_model.rowCount())
        self.setEnabled(False)
        self.buildStarted.emit()

        structure_template = self._structure_template
        structure_signature = self._structure_signature

        def task():
            return build_tree_data(
                cols,
                structure_template=structure_template,
                structure_signature=structure_signature,
                **self._build_scope,
            )

        def on_done(future):
            self._on_tree_ready(future, cols, build_id)

        mw.taskman.with_progress(
            task,
            on_done,
            parent=self,
            label='Collecting data and building tree\nThis can take a while for large collections',
            immediate=True,
        )

    def _on_tree_ready(self, future, cols, build_id):
        if build_id != self._build_id:
            return

        try:
            result = future.result()
        except Exception as exc:
            self.setEnabled(True)
            self.buildFinished.emit()
            showWarning("Syllabus could not build the tree:\n\n{}".format(exc))
            return

        self.tree = result.tree
        self._structure_template = result.structure_template
        self._structure_signature = result.structure_signature

        self.render_tree(cols)

    def render_tree(self, cols=None):
        if not self.tree:
            return

        cols = list(cols or self._current_cols)
        self.source_model.removeRows(0, self.source_model.rowCount())
        top_level_nodes = [self.tree] if self._build_scope["include_root"] else self.tree.children
        self._populateTree(top_level_nodes, self.source_model.invisibleRootItem(), cols=cols)
        self._restoring_expansion = True
        try:
            self.expandToDepth(1)
        finally:
            self._restoring_expansion = False
        for i in range(len(HEADER_LABELS)):
            self.resizeColumnToContents(i)
            self.setColumnHidden(i, i not in cols)

        self.setEnabled(True)
        self.buildFinished.emit()
        self.refresh_view_layout()

    def expanded_node_keys(self):
        keys = []
        self._append_expanded_node_keys(QModelIndex(), keys)
        return keys

    def _append_expanded_node_keys(self, proxy_parent, keys):
        for row in range(self.proxy_model.rowCount(proxy_parent)):
            proxy_index = self.proxy_model.index(row, NAME, proxy_parent)
            node = self.selected_node(proxy_index)
            if node and self.isExpanded(proxy_index):
                keys.append(self.node_key(node))
            self._append_expanded_node_keys(proxy_index, keys)

    def restore_expanded_node_keys(self, keys):
        key_set = set(keys or [])
        self._restoring_expansion = True
        try:
            self.collapseAll()
            self._restore_expanded_node_keys(QModelIndex(), key_set)
            self.refresh_view_layout()
        finally:
            self._restoring_expansion = False

    def _restore_expanded_node_keys(self, proxy_parent, key_set):
        for row in range(self.proxy_model.rowCount(proxy_parent)):
            proxy_index = self.proxy_model.index(row, NAME, proxy_parent)
            node = self.selected_node(proxy_index)
            if node and self.node_key(node) in key_set:
                self.setExpanded(proxy_index, True)
            self._restore_expanded_node_keys(proxy_index, key_set)

    def node_key(self, node):
        return '{}\t{}\t{}'.format(node.kind, node.deck, node.name)

    def emit_expansion_changed(self):
        if not self._restoring_expansion:
            self.expansionChanged.emit()
        
    def set_filter_text(self, text):
        self.proxy_model.set_filter_text(text)
        if text:
            self.expandAll()
        else:
            self.expandToDepth(1)
        self.refresh_view_layout()

    def set_hide_empty(self, hide_empty):
        self.proxy_model.set_hide_empty(hide_empty)
        self.refresh_view_layout()

    def set_build_scope(self, include_decks=True, include_tags=True, include_root=True):
        self.gen_tree(
            cols=self._current_cols,
            build_scope={
                "include_decks": include_decks,
                "include_tags": include_tags,
                "include_root": include_root,
            },
        )

    def refresh_view_layout(self):
        self.doItemsLayout()
        self.updateGeometries()
        self.viewport().update()
        self.updateGeometry()
        QTimer.singleShot(0, self.doItemsLayout)
        QTimer.singleShot(0, self.updateGeometries)
        QTimer.singleShot(0, self.viewport().update)
    
    def expand_tree(self):
        target_depth = self.next_collapsed_depth()
        if target_depth is None:
            return
        self.expand_collapsed_at_depth(QModelIndex(), 0, target_depth)
        self.refresh_view_layout()

    def collapse_tree(self):
        depth = self.deepest_expanded_depth()
        if depth <= 0:
            self.collapseAll()
        else:
            self.collapse_expanded_at_depth(QModelIndex(), 0, depth)
        self.refresh_view_layout()

    def expand_all_tree(self):
        self.expandAll()
        self.refresh_view_layout()

    def collapse_all_tree(self):
        self.collapseAll()
        self.refresh_view_layout()

    def next_collapsed_depth(self):
        return self._next_collapsed_depth(QModelIndex(), 0)

    def _next_collapsed_depth(self, proxy_parent, depth):
        result = None
        for row in range(self.proxy_model.rowCount(proxy_parent)):
            proxy_index = self.proxy_model.index(row, NAME, proxy_parent)
            has_children = self.proxy_model.rowCount(proxy_index) > 0
            if has_children and not self.isExpanded(proxy_index):
                result = depth if result is None else min(result, depth)
            if self.isExpanded(proxy_index):
                child_result = self._next_collapsed_depth(proxy_index, depth + 1)
                if child_result is not None:
                    result = child_result if result is None else min(result, child_result)
        return result

    def expand_collapsed_at_depth(self, proxy_parent, depth, target_depth):
        for row in range(self.proxy_model.rowCount(proxy_parent)):
            proxy_index = self.proxy_model.index(row, NAME, proxy_parent)
            if depth == target_depth:
                if self.proxy_model.rowCount(proxy_index) > 0:
                    self.setExpanded(proxy_index, True)
            elif self.isExpanded(proxy_index):
                self.expand_collapsed_at_depth(proxy_index, depth + 1, target_depth)

    def deepest_expanded_depth(self):
        return self._deepest_expanded_depth(QModelIndex(), 0)

    def _deepest_expanded_depth(self, proxy_parent, depth):
        max_depth = -1
        for row in range(self.proxy_model.rowCount(proxy_parent)):
            proxy_index = self.proxy_model.index(row, NAME, proxy_parent)
            if self.isExpanded(proxy_index):
                max_depth = max(max_depth, depth)
                max_depth = max(
                    max_depth,
                    self._deepest_expanded_depth(proxy_index, depth + 1),
                )
        return max_depth

    def collapse_expanded_at_depth(self, proxy_parent, depth, target_depth):
        for row in range(self.proxy_model.rowCount(proxy_parent)):
            proxy_index = self.proxy_model.index(row, NAME, proxy_parent)
            if depth == target_depth:
                self.setExpanded(proxy_index, False)
            elif self.isExpanded(proxy_index):
                self.collapse_expanded_at_depth(proxy_index, depth + 1, target_depth)
    
    def selected_node(self, index=None):
        if index is None:
            indexes = self.selectedIndexes()
            if not indexes:
                return None
            index = indexes[0]

        if not index.isValid():
            return None

        source_index = self.proxy_model.mapToSource(index)
        name_index = self.source_model.index(source_index.row(), NAME, source_index.parent())
        return self.source_model.data(name_index, NODE_ROLE)

    def search_for_node(self, node):
        if node.kind == 'collection':
            return ''
        if node.kind == 'deck':
            return 'deck:{}'.format(self.quote_search_value(node.name))
        if node.kind == 'tag':
            return 'tag:{}'.format(self.quote_search_value(node.name))
        return ''

    def search_for_column(self, column_id):
        column = COLUMN_BY_ID.get(column_id)
        if column:
            return column.search or ''
        return ''

    def search_for_node_and_column(self, node, column_id=None, extra_search=None):
        terms = []
        scope = self.search_for_node(node)
        if scope:
            terms.append(scope)

        column_search = self.search_for_column(column_id) if column_id is not None else ''
        if column_search:
            terms.append(column_search)
        if extra_search:
            terms.append(extra_search)
        return ' '.join(terms)

    def quote_search_value(self, value):
        return '"{}"'.format(value.replace('\\', '\\\\').replace('"', '\\"'))
    
    def open_node_in_browser(self, node, column_id=None, extra_search=None):
        query = self.search_for_node_and_column(
            node,
            column_id=column_id,
            extra_search=extra_search,
        )
        if not query:
            return

        browser = aqt.dialogs.open("Browser", mw)
        browser.search_for(query)
    
    def copy_text(self, text):
        QApplication.clipboard().setText(text)
        tooltip("Copied")
    
    def show_context_menu(self, pos):
        index = self.indexAt(pos)
        node = self.selected_node(index)
        if node is None:
            return

        source_index = self.proxy_model.mapToSource(index)
        column_id = source_index.column()

        menu = QMenu(self)
        open_action = menu.addAction("Open in Browser")
        open_action.setEnabled(bool(self.search_for_node_and_column(node, column_id)))
        open_new_action = menu.addAction("Open New")
        open_learning_action = menu.addAction("Open Learning")
        open_due_action = menu.addAction("Open Due")
        open_suspended_action = menu.addAction("Open Suspended")
        menu.addSeparator()
        export_subtree_action = menu.addAction("Export Subtree")
        copy_name_action = menu.addAction("Copy Name")
        copy_search_action = menu.addAction("Copy Search")
        copy_search_action.setEnabled(bool(self.search_for_node_and_column(node, column_id)))
        menu.addSeparator()
        expand_action = menu.addAction("Expand All")
        collapse_action = menu.addAction("Collapse All")

        action = menu.exec(self.viewport().mapToGlobal(pos))
        if action == open_action:
            self.open_node_in_browser(node, column_id=column_id)
        elif action == open_new_action:
            self.open_node_in_browser(node, extra_search='is:new')
        elif action == open_learning_action:
            self.open_node_in_browser(node, extra_search='is:learn')
        elif action == open_due_action:
            self.open_node_in_browser(node, extra_search='is:due')
        elif action == open_suspended_action:
            self.open_node_in_browser(node, extra_search='is:suspended')
        elif action == export_subtree_action:
            self.exportSubtreeRequested.emit(node)
        elif action == copy_name_action:
            self.copy_text(node.name)
        elif action == copy_search_action:
            self.copy_text(self.search_for_node_and_column(node, column_id))
        elif action == expand_action:
            self.expand_all_tree()
        elif action == collapse_action:
            self.collapse_all_tree()

    def visible_export_rows(self):
        rows = []
        self._append_visible_export_rows(QModelIndex(), rows)
        return rows

    def _append_visible_export_rows(self, proxy_parent, rows):
        for row in range(self.proxy_model.rowCount(proxy_parent)):
            proxy_index = self.proxy_model.index(row, NAME, proxy_parent)
            node = self.selected_node(proxy_index)
            if node:
                rows.append(node_to_row(node))
            self._append_visible_export_rows(proxy_index, rows)
    
    def _populateTree(self, children, parent, cols=DEFAULT_COLUMNS):
        for child in children:
            row = node_to_q_row(child, cols=cols)
            parent.appendRow(row)
            self._populateTree(child.children, row[0], cols=cols)

    def on_double_click(self, node_index):
        node = self.selected_node(node_index)
        if node:
            source_index = self.proxy_model.mapToSource(node_index)
            self.open_node_in_browser(node, column_id=source_index.column())
