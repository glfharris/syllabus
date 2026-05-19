import os

from aqt import qt

from .columns import COLUMN_BY_ID, HEADER_LABELS, NAME, DECK, KIND

NODE_ROLE = int(qt.Qt.ItemDataRole.UserRole) + 1
SORT_ROLE = int(qt.Qt.ItemDataRole.UserRole) + 2
RIGHT_ALIGN = qt.Qt.AlignmentFlag.AlignRight | qt.Qt.AlignmentFlag.AlignVCenter


def node_to_q_row(node, cols):
    q_row = [qt.QStandardItem() for _ in HEADER_LABELS]
    for column_id in cols:
        q_row[column_id] = q_item_for_node(node, column_id)
    return q_row


def q_item_for_node(node, column_id):
    if column_id == NAME:
        return q_name(node)
    if column_id == KIND:
        return q_text(node.kind, sort_value=node.kind)
    if column_id == DECK:
        return q_text(node.deck_name, sort_value=node.deck_name.lower())

    column = COLUMN_BY_ID[column_id]
    value = node.data.get(column.key)
    if value is None:
        return qt.QStandardItem()
    if column.precision is not None:
        return q_percent(value, column.precision)
    return q_count(value, column.color)


def q_name(node):
    item = qt.QStandardItem(node.display_name)
    icon_path = os.path.join(os.path.dirname(__file__), 'icons', '{}.svg'.format(node.kind))
    item.setIcon(qt.QIcon(icon_path))
    item.setData(node, NODE_ROLE)
    item.setData(node.name.lower(), SORT_ROLE)
    if node.display_name != node.name:
        item.setToolTip(node.name)
    return item


def q_text(value, sort_value=None):
    item = qt.QStandardItem(str(value))
    item.setData(sort_value if sort_value is not None else value, SORT_ROLE)
    return item


def q_count(value, color=None):
    item = qt.QStandardItem(str(value))
    item.setTextAlignment(RIGHT_ALIGN)
    item.setData(value, SORT_ROLE)
    if color:
        item.setForeground(qt.QColor(*color))
    return item


def q_percent(value, precision):
    item = qt.QStandardItem('{:.{}%}'.format(value, precision))
    item.setTextAlignment(RIGHT_ALIGN)
    item.setData(value, SORT_ROLE)
    return item
