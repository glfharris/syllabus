class Node:
    def __init__(self, name, kind, deck, deck_name=None):
        self.deck = deck
        self.deck_name = deck_name or str(deck)
        self.name = name
        self.display_name = name.rsplit('::', 1)[-1]
        self.kind = kind
        self.children = []
        self.data = {}
        self.total = 0
    
    def __repr__(self):
        return '<{} - {}>'.format(self.kind, self.name)

    def clear_data(self):
        self.data = {}
        for child in self.children:
            child.clear_data()

    def clone_structure(self):
        node = Node(self.name, self.kind, self.deck, deck_name=self.deck_name)
        node.display_name = self.display_name
        node.total = self.total
        node.children = [child.clone_structure() for child in self.children]
        return node
    
    def acquire_child_tags(self, context):
        parent_name = self.name if self.kind == 'tag' else None
        deck = self.deck
        if self.kind == 'collection' and not context.include_decks:
            deck = 'collection'

        for tag_name in context.child_tags(deck, parent_name):
            tag = Node(tag_name, 'tag', self.deck, deck_name=self.deck_name)
            self.children.append(tag)

        for child in self.children:
            child.acquire_child_tags(context=context)

    def acquire_child_decks(self, context):
        if self.kind not in ('deck', 'collection'):
            return

        for deck_id, deck_name in context.child_decks(self.name):
            self.children.append(Node(deck_name, 'deck', deck_id, deck_name=deck_name))

        for child in self.children:
            child.acquire_child_decks(context=context)
