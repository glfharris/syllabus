from aqt import mw

def note_count(deck, tag=''):
    return mw.col.db.scalar('select count() '
                            'from cards inner join notes '
                            'on cards.nid = notes.id '
                            'where cards.did = "' + deck + '" and notes.tags like "%' + tag + '%"')

def _card_note_query(condition=None, deck=None, tag=None):
    query = 'select count() from (cards inner join notes on cards.nid = notes.id) where 1 '
    
    if deck and deck is not 'collection':
        query += 'and cards.did == {} '.format(deck)
    if tag:
        query += 'and notes.tags like "%{}%" '.format(tag)
    if condition:
        query += 'and {}'.format(condition)
        
    res = mw.col.db.scalar(query)
    return res

def count_new(deck=None, tag=None):
    cond = 'cards.queue == 0'
    return _card_note_query(condition=cond, deck=deck, tag=tag)

def count_learning(deck=None, tag=None):
    cond = 'cards.queue == 1'
    return _card_note_query(condition=cond, deck=deck, tag=tag)

def count_young(deck=None, tag=None):
    cond = 'cards.queue == 2 and cards.ivl < 21'
    return _card_note_query(condition=cond, deck=deck, tag=tag)

def count_mature(deck=None, tag=None):
    cond = 'cards.queue == 2 and cards.ivl >= 21'
    return _card_note_query(condition=cond, deck=deck, tag=tag)

def count_total(deck=None, tag=None):
    return _card_note_query(deck=deck, tag=tag)
