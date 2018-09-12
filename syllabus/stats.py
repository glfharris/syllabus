from aqt import mw

def note_count(deck, tag=''):
    return mw.col.db.scalar('select count() '
                            'from cards inner join notes '
                            'on cards.nid = notes.id '
                            'where cards.did = "' + deck + '" and notes.tags like "%' + tag + '%"')
