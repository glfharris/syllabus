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

def _r_query(select='*', rev_cond=None):
    conds = ' and '.join(rev_cond)
    if rev_cond:
        rev_table = '(select {} from revlog where {}) as revlog'.format(select, conds)
    else:
        rev_table = '(select {} from revlog) as revlog'.format(select)
    
    return rev_table

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

def retention(deck=None, tag=None, retention='mature'):
    if retention == 'mature':
        last_ivl = '>= 21'
    elif retention == 'young':
        last_ivl = '< 21'
    else:
        last_ivl = None

    if last_ivl:
        last_ivl_cond = 'revlog.lastIvl {}'.format(last_ivl)
    else:
        last_ivl_cond = '1'

    c_n_table = _as(_c_n_query('cards.id as cid', deck=deck, tag=tag), 'cards_notes')
    passed_rev_table = _r_query(rev_cond=['revlog.ease > 1 and revlog.type == 1', last_ivl_cond])
    flunked_rev_table = _r_query(rev_cond=['revlog.ease == 1 and revlog.type == 1', last_ivl_cond])

    passed_query = ' '.join(['select count() from', passed_rev_table, 'inner join', c_n_table, 'on revlog.cid=cards_notes.cid'])
    flunked_query = ' '.join(['select count() from', flunked_rev_table, 'inner join', c_n_table, 'on revlog.cid=cards_notes.cid'])

    passed = mw.col.db.scalar(passed_query)
    flunked = mw.col.db.scalar(flunked_query)

    return (passed / (passed + flunked))