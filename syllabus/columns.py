from dataclasses import dataclass


@dataclass(frozen=True)
class Column:
    id: int
    label: str
    key: str | None = None
    group: str | None = None
    simple: bool = False
    precision: int | None = None
    color: tuple[int, int, int] | None = None
    search: str | None = None
    derived: bool = False


NAME = 0
KIND = 1
DECK = 2
TOTAL = 3
NEW = 4
LEARNING = 5
YOUNG = 6
MATURE = 7
BURIED = 8
SUSPENDED = 9
EASE = 10
YOU_RENT = 11
MAT_RENT = 12
TOT_RENT = 13
PCT_NEW = 14
PCT_LEARNING = 15
PCT_MATURE = 16
PCT_SUSPENDED = 17

COLUMNS = [
    Column(NAME, 'Name'),
    Column(KIND, 'Kind', group='Misc'),
    Column(DECK, 'Deck', group='Misc'),
    Column(TOTAL, 'Total', 'total', simple=True),
    Column(NEW, 'New', 'new', simple=True, color=(33, 99, 181), search='is:new'),
    Column(LEARNING, 'Learning', 'learning', simple=True, color=(173, 64, 49), search='is:learn'),
    Column(YOUNG, 'Young', 'young', simple=True, color=(79, 143, 79), search='is:review prop:ivl<21'),
    Column(MATURE, 'Mature', 'mature', simple=True, color=(45, 116, 68), search='is:review prop:ivl>=21'),
    Column(BURIED, 'Buried', 'buried', group='Unqueued', simple=True, search='is:buried'),
    Column(SUSPENDED, 'Suspended', 'suspended', group='Unqueued', simple=True, search='is:suspended'),
    Column(EASE, 'Ease', 'ease', precision=0),
    Column(YOU_RENT, 'Young Retention', 'young_retention', group='Retention', precision=2),
    Column(MAT_RENT, 'Mature Retention', 'mature_retention', group='Retention', precision=2),
    Column(TOT_RENT, 'Total Retention', 'total_retention', group='Retention', precision=2),
    Column(PCT_NEW, '% New', 'pct_new', group='Compare', precision=1, derived=True),
    Column(PCT_LEARNING, '% Learning', 'pct_learning', group='Compare', precision=1, derived=True),
    Column(PCT_MATURE, '% Mature', 'pct_mature', group='Compare', precision=1, derived=True),
    Column(PCT_SUSPENDED, '% Suspended', 'pct_suspended', group='Compare', precision=1, derived=True),
]

COLUMN_BY_ID = {column.id: column for column in COLUMNS}
HEADER_LABELS = [column.label for column in COLUMNS]
DEFAULT_COLUMNS = [NAME, TOTAL, NEW, LEARNING, YOUNG, MATURE]
SIMPLE_COLUMN_KEYS = {
    column.id: column.key
    for column in COLUMNS
    if column.simple and column.key
}

COLUMN_SETTINGS = [
    ('Total', TOTAL),
    ('New', NEW),
    ('Learning', LEARNING),
    ('Young', YOUNG),
    ('Mature', MATURE),
    ('Ease', EASE),
    ('Unqueued', [('Buried', BURIED), ('Suspended', SUSPENDED)]),
    (
        'Retention',
        [
            ('Young Retention', YOU_RENT),
            ('Mature Retention', MAT_RENT),
            ('Total Retention', TOT_RENT),
        ],
    ),
    (
        'Compare',
        [
            ('% New', PCT_NEW),
            ('% Learning', PCT_LEARNING),
            ('% Mature', PCT_MATURE),
            ('% Suspended', PCT_SUSPENDED),
        ],
    ),
    ('Misc', [('Kind', KIND), ('Deck', DECK)]),
]
