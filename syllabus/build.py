from collections import defaultdict
from dataclasses import dataclass

from aqt import mw

from .columns import (
    BURIED,
    COLUMN_BY_ID,
    EASE,
    LEARNING,
    MAT_RENT,
    MATURE,
    NEW,
    SIMPLE_COLUMN_KEYS,
    SUSPENDED,
    TOT_RENT,
    TOTAL,
    YOU_RENT,
    YOUNG,
)
from .info import hierarchy_names, parent_name
from .node import Node
from .stats import ease, retention


@dataclass
class BuildResult:
    tree: Node
    structure_signature: tuple
    structure_template: Node


class SyllabusBuildContext:
    def __init__(self, cols, collection=None, include_decks=True, include_tags=True, include_root=True):
        self.collection = collection or mw.col
        self.include_decks = include_decks
        self.include_tags = include_tags
        self.include_root = include_root
        self.cols = set(cols)
        self.visible_simple_cols = self.cols & set(SIMPLE_COLUMN_KEYS)
        self.derived_cols = {
            column_id for column_id in self.cols
            if COLUMN_BY_ID[column_id].derived
        }
        self.count_cols = self.visible_simple_cols | self.required_simple_cols() | {TOTAL}
        self.decks = self._load_decks()
        self.deck_children = self._load_deck_children()
        self.deck_ancestors = self._load_deck_ancestors()
        self.tags_by_deck_name = defaultdict(set)
        self.simple_counts = defaultdict(lambda: defaultdict(int))
        self._scan_cards()
        self.child_decks_by_parent = self._load_child_decks_by_parent()
        self.child_tags_by_deck_parent = self._load_child_tags_by_deck_parent()
        self.structure_signature = self._structure_signature()

    def _load_decks(self):
        return {
            str(deck.id): deck.name
            for deck in self.collection.decks.all_names_and_ids()
        }

    def _load_deck_children(self):
        children = {'collection': tuple(self.decks)}
        for deck_id, deck_name in self.decks.items():
            try:
                child_ids = self.collection.decks.deck_and_child_ids(int(deck_id))
                children[deck_id] = tuple(str(child_id) for child_id in child_ids)
            except AttributeError:
                prefix = deck_name + '::'
                children[deck_id] = tuple(
                    other_id for other_id, other_name in self.decks.items()
                    if other_id == deck_id or other_name.startswith(prefix)
                )
        return children

    def _load_deck_ancestors(self):
        ancestors = defaultdict(set)
        ancestors['collection'].add('collection')
        for deck_id in self.decks:
            ancestors[deck_id].add('collection')

        for scope_deck, child_ids in self.deck_children.items():
            for child_id in child_ids:
                ancestors[child_id].add(scope_deck)

        return ancestors

    def _scan_cards(self):
        rows = self.collection.db.all(
            '''
            select cards.did, cards.odid, cards.queue, cards.ivl, notes.tags
            from cards
            inner join notes on cards.nid = notes.id
            '''
        )

        for did, odid, queue, interval, tags in rows:
            scope_decks = self._scope_decks(did, odid)
            tag_names = self._hierarchical_tags(tags)

            for deck_id in scope_decks:
                self._add_simple_count(('deck', deck_id), queue, interval)
                self.tags_by_deck_name[deck_id].update(tag_names)

                for tag in tag_names:
                    self._add_simple_count(('tag', deck_id, tag), queue, interval)

            self._add_simple_count(('collection', 'collection'), queue, interval)
            self.tags_by_deck_name['collection'].update(tag_names)
            for tag in tag_names:
                self._add_simple_count(('tag', 'collection', tag), queue, interval)

    def _scope_decks(self, did, odid):
        card_decks = {str(did)}
        if odid:
            card_decks.add(str(odid))

        scope_decks = set()
        for deck_id in card_decks:
            scope_decks.update(self.deck_ancestors.get(deck_id, {'collection'}))
        scope_decks.discard('collection')
        return scope_decks

    def _hierarchical_tags(self, tags):
        names = set()
        for tag in self.collection.tags.split(tags or ''):
            names.update(hierarchy_names(tag))
        return names

    def _add_simple_count(self, key, queue, interval):
        if not self.count_cols:
            return

        stats = self.simple_counts[key]
        if TOTAL in self.count_cols:
            stats['total'] += 1
        if NEW in self.count_cols and queue == 0:
            stats['new'] += 1
        if LEARNING in self.count_cols and queue in (1, 3):
            stats['learning'] += 1
        if YOUNG in self.count_cols and queue == 2 and interval < 21:
            stats['young'] += 1
        if MATURE in self.count_cols and queue == 2 and interval >= 21:
            stats['mature'] += 1
        if BURIED in self.count_cols and queue in (-2, -3):
            stats['buried'] += 1
        if SUSPENDED in self.count_cols and queue == -1:
            stats['suspended'] += 1

    def required_simple_cols(self):
        required = set()
        for column_id in self.derived_cols:
            key = COLUMN_BY_ID[column_id].key
            required.add(TOTAL)
            if key == 'pct_new':
                required.add(NEW)
            elif key == 'pct_learning':
                required.add(LEARNING)
            elif key == 'pct_mature':
                required.add(MATURE)
            elif key == 'pct_suspended':
                required.add(SUSPENDED)
        return required

    def child_decks(self, parent_name):
        return self.child_decks_by_parent.get(parent_name, ())

    def child_tags(self, deck, parent_name):
        return self.child_tags_by_deck_parent.get((deck, parent_name), ())

    def _load_child_decks_by_parent(self):
        child_decks = defaultdict(list)
        for deck_id, deck_name in self.decks.items():
            parent = parent_name(deck_name) or 'collection'
            child_decks[parent].append((deck_id, deck_name))

        for children in child_decks.values():
            children.sort(key=lambda child: child[1], reverse=True)

        return child_decks

    def _load_child_tags_by_deck_parent(self):
        child_tags = defaultdict(list)
        for deck_id, tag_names in self.tags_by_deck_name.items():
            for tag_name in tag_names:
                parent = parent_name(tag_name)
                child_tags[(deck_id, parent)].append(tag_name)

        for children in child_tags.values():
            children.sort(reverse=True)

        return child_tags

    def apply_simple_counts(self, node, cols):
        if node.kind == 'collection':
            key = ('collection', 'collection')
        elif node.kind == 'deck':
            key = ('deck', node.deck)
        elif node.kind == 'tag':
            key = ('tag', node.deck, node.name)
        else:
            return

        stats = self.simple_counts.get(key, {})
        node.total = stats.get('total', 0)
        for column in self.visible_simple_cols & set(cols):
            node.data[SIMPLE_COLUMN_KEYS[column]] = stats.get(SIMPLE_COLUMN_KEYS[column], 0)

        for column_id in cols:
            column = COLUMN_BY_ID[column_id]
            if column.derived:
                node.data[column.key] = self.derived_value(column.key, stats)

    def derived_value(self, key, stats):
        total = stats.get('total', 0)
        if not total:
            return None
        if key == 'pct_new':
            return stats.get('new', 0) / total
        if key == 'pct_learning':
            return stats.get('learning', 0) / total
        if key == 'pct_mature':
            return stats.get('mature', 0) / total
        if key == 'pct_suspended':
            return stats.get('suspended', 0) / total
        return None

    def apply_expensive_stats(self, node, cols):
        deck, tag = self.query_scope(node)
        for column_id in cols:
            column = COLUMN_BY_ID[column_id]
            if column_id == EASE:
                value = ease(deck=deck, tag=tag, col=self.collection)
                node.data[column.key] = value / 1000 if value else None
            elif column_id == YOU_RENT:
                self.apply_retention(node, column.key, deck, tag, 'young')
            elif column_id == MAT_RENT:
                self.apply_retention(node, column.key, deck, tag, 'mature')
            elif column_id == TOT_RENT:
                self.apply_retention(node, column.key, deck, tag, 'total')

    def apply_retention(self, node, key, deck, tag, retention_kind):
        try:
            node.data[key] = retention(
                deck=deck,
                tag=tag,
                retention=retention_kind,
                col=self.collection,
            )
        except ZeroDivisionError:
            node.data[key] = None

    def query_scope(self, node):
        if node.kind == 'collection':
            return None, None
        if node.kind == 'deck':
            return list(self.deck_children[node.deck]), None
        if node.kind == 'tag':
            if node.deck == 'collection':
                return None, node.name
            return list(self.deck_children[node.deck]), node.name
        return None, None

    def compute_columns(self, node, cols):
        self.apply_simple_counts(node, cols)
        self.apply_expensive_stats(node, cols)
        for child in node.children:
            self.compute_columns(child, cols)

    def _structure_signature(self):
        tag_signature = tuple(
            (deck_id, tuple(sorted(tags)))
            for deck_id, tags in sorted(self.tags_by_deck_name.items())
        )
        return (
            tuple(sorted(self.decks.items())),
            tag_signature,
            self.include_decks,
            self.include_tags,
            self.include_root,
        )


def build_tree_data(
    cols,
    structure_template=None,
    structure_signature=None,
    collection=None,
    include_decks=True,
    include_tags=True,
    include_root=True,
):
    context = SyllabusBuildContext(
        cols,
        collection=collection,
        include_decks=include_decks,
        include_tags=include_tags,
        include_root=include_root,
    )
    if structure_template and structure_signature == context.structure_signature:
        tree = structure_template.clone_structure()
    else:
        tree = Node('collection', 'collection', 'collection', deck_name='collection')
        if include_decks:
            tree.acquire_child_decks(context=context)
        if include_tags:
            tree.acquire_child_tags(context=context)

    tree.clear_data()
    if include_root:
        context.compute_columns(tree, cols)
    else:
        for child in tree.children:
            context.compute_columns(child, cols)
    return BuildResult(
        tree=tree,
        structure_signature=context.structure_signature,
        structure_template=tree.clone_structure(),
    )
