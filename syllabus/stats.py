from aqt import mw

def _c_n_query(select, deck=None, tag=None, card_cond=None, card_sel='*', note_cond=None, note_sel='*'):
    n_conds = []
    c_conds = []
    if tag:
        n_conds.append('notes.tags like "% {}%"'.format(tag))
    if deck:
        c_conds.append('cards.did in ({})'.format(', '.join(deck)))
    
    if card_cond:
        c_conds += card_cond
    if note_cond:
        n_conds += note_cond
    
    n_conds = ' and '.join(n_conds)
    c_conds = ' and '.join(c_conds)


    if c_conds:
        card_table = '(select {} from cards where {}) as cards'.format(card_sel, c_conds)
    elif c_conds is None and card_sel is not '*':
        card_table = '(select {} from cards) as cards'.format(card_sel)
    else:
        card_table = 'cards'
    
    if n_conds:
        note_table = '(select {} from notes where {}) as notes'.format(note_sel, n_conds)
    elif n_conds is None and note_sel is not '*':
        note_table = '(select {} from notes) as notes'.format(note_sel)
    else:
        note_table = 'notes'
    
    query = ['select', select, 'from', card_table, 'inner join', note_table, 'on cards.nid=notes.id']
    return ' '.join(query)

def _as(subquery, q_as):
    return '({}) as {}'.format(subquery, q_as)

def total(deck=None, tag=None):
    return mw.col.db.scalar(_c_n_query('count()', deck=deck, tag=tag))

def new(deck=None, tag=None):
    cond = 'cards.queue == 0'
    return mw.col.db.scalar(_c_n_query('count()', deck=deck, tag=tag, card_cond=[cond]))

def learning(deck=None, tag=None):
    cond = '(cards.queue == 1 or cards.queue == 3)'
    return mw.col.db.scalar(_c_n_query('count()', deck=deck, tag=tag, card_cond=[cond]))

def young(deck=None, tag=None):
    cond = 'cards.queue == 2 and cards.ivl < 21'
    return mw.col.db.scalar(_c_n_query('count()', deck=deck, tag=tag, card_cond=[cond]))

def mature(deck=None, tag=None):
    cond = 'cards.queue == 2 and cards.ivl >= 21'
    return mw.col.db.scalar(_c_n_query('count()', deck=deck, tag=tag, card_cond=[cond]))

def suspended(deck=None, tag=None):
    cond = 'cards.queue == -1'
    return mw.col.db.scalar(_c_n_query('count()', deck=deck, tag=tag, card_cond=[cond]))

def buried(deck=None, tag=None):
    cond = '(cards.queue == -2 or cards.queue == -3)'
    return mw.col.db.scalar(_c_n_query('count()', deck=deck, tag=tag, card_cond=[cond]))

def ease(deck=None, tag=None):
    inner_q = _as(_c_n_query('cards.factor as factor', deck=deck, tag=tag, card_cond=['cards.factor > 0']), 'cards_notes')
    tmp = 'select avg(factor) from {}'.format(inner_q)
    return mw.col.db.scalar(tmp)