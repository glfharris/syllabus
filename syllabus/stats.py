from aqt import mw


def collection_or_default(col=None):
    return col or mw.col


def _sql_list(values):
    return ','.join('?' for _ in values)


def _escape_like(value):
    return (
        value
        .replace('\\', '\\\\')
        .replace('%', '\\%')
        .replace('_', '\\_')
    )


def _card_note_conditions(deck=None, tag=None, card_cond=None, note_cond=None):
    n_conds = []
    c_conds = []
    n_params = []
    c_params = []

    if tag:
        escaped_tag = _escape_like(tag)
        n_conds.append("(notes.tags like ? escape '\\' or notes.tags like ? escape '\\')")
        n_params.extend([f'% {escaped_tag} %', f'% {escaped_tag}::%'])

    if deck:
        deck_ids = [int(deck_id) for deck_id in deck]
        placeholders = _sql_list(deck_ids)
        c_conds.append(
            f'(cards.did in ({placeholders}) or cards.odid in ({placeholders}))'
        )
        c_params.extend(deck_ids + deck_ids)
    
    if card_cond:
        c_conds += card_cond
    if note_cond:
        n_conds += note_cond
    
    conds = c_conds + n_conds
    params = c_params + n_params
    if conds:
        return ' where ' + ' and '.join(conds), params

    return '', params


def _c_n_scalar(select, deck=None, tag=None, card_cond=None, note_cond=None, col=None):
    where, params = _card_note_conditions(
        deck=deck,
        tag=tag,
        card_cond=card_cond,
        note_cond=note_cond,
    )
    query = f'''
        select {select}
        from cards
        inner join notes on cards.nid = notes.id
        {where}
    '''
    return collection_or_default(col).db.scalar(query, *params)

def ease(deck=None, tag=None, col=None):
    return _c_n_scalar(
        'avg(cards.factor)',
        deck=deck,
        tag=tag,
        card_cond=['cards.factor > 0'],
        col=col,
    )

def retention(deck=None, tag=None, retention='mature', col=None):
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

    card_note_where, params = _card_note_conditions(deck=deck, tag=tag)
    base_where = card_note_where[7:] if card_note_where.startswith(' where ') else '1'

    passed_query = f'''
        select count()
        from revlog
        inner join cards on revlog.cid = cards.id
        inner join notes on cards.nid = notes.id
        where revlog.ease > 1 and revlog.type = 1 and {last_ivl_cond} and {base_where}
    '''
    flunked_query = f'''
        select count()
        from revlog
        inner join cards on revlog.cid = cards.id
        inner join notes on cards.nid = notes.id
        where revlog.ease = 1 and revlog.type = 1 and {last_ivl_cond} and {base_where}
    '''

    collection = collection_or_default(col)
    passed = collection.db.scalar(passed_query, *params)
    flunked = collection.db.scalar(flunked_query, *params)

    return (passed / (passed + flunked))
