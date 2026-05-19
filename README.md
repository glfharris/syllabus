# Syllabus

An Anki add-on for exploring collection statistics by deck and tag.

Open it from `Tools > Syllabus`.

<img src="https://www.github.com/glfharris/syllabus/blob/master/syllabus.jpg&raw=true">

## Features

- Tree view of collection, deck, and tag statistics
- Selectable columns for counts, retention, ease, and comparison percentages
- Optional build scope: root, decks, tags
- Filter, hide empty rows, expand/collapse, and persisted layout state
- Double-click or right-click rows to open matching cards in the Browser
- Export all rows, the selected subtree, or the visible filtered view to CSV

## Build

Requires `just`.

```sh
just build
```

This creates `build/anki-syllabus-v21.ankiaddon`.

## Development

```sh
just test
```

Installs the add-on into `~/.local/share/Anki2/addons21/syllabus-test` and starts Anki.
