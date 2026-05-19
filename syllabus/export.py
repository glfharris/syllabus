def collate_tree(node):
    rows = []
    append_node(node, rows)
    return rows


def append_node(node, rows):
    rows.append(node_to_row(node))
    for child in node.children:
        append_node(child, rows)


def node_to_row(node):
    row = {'name': node.name, 'deck': node.deck, 'kind': node.kind}
    row.update(node.data)
    return row
