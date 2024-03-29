# anki-export

![Github Actions](https://github.com/patarapolw/anki-export/actions/workflows/test.yml/badge.svg)
[![PyPI version shields.io](https://img.shields.io/pypi/v/anki-export.svg)](https://pypi.python.org/pypi/anki-export/)
[![PyPI license](https://img.shields.io/pypi/l/anki-export.svg)](https://pypi.python.org/pypi/anki-export/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/anki-export.svg)](https://pypi.python.org/pypi/anki-export/)

Export your Anki \*.apkg to Python. Read Anki \*.apkg in Python.

## Example

```python
from anki_export import ApkgReader
import pyexcel_xlsxwx

with ApkgReader('test.apkg') as apkg:
    pyexcel_xlsxwx.save_data('test.xlsx', apkg.export(), config={'format': None})
```

See real running example at [`/__extras__/blank-install/to-xlsx.py`](/__extras__/blank-install).

## Installation

```commandline
$ pip install anki-export
```

## Why?

- \*.apkg is quite well structured, convincing me to use this format more.
- Allow you to use \*.apkg programmatically in Python.
- Might be less buggy than https://github.com/patarapolw/AnkiTools

## My other projects to create SRS flashcards outside Anki

- [srs-sqlite](https://github.com/patarapolw/srs-sqlite) - A simple SRS app using Markdown/HandsOnTable/SQLite
- [jupyter-flashcards](https://github.com/patarapolw/jupyter-flashcards) - Excel-powered. Editable in Excel. SRS-enabled.
- [gflashcards](https://github.com/patarapolw/gflashcards) - A simple app to make formatted flashcards from Google Sheets. SRS-not-yet-enabled.
- [HanziLevelUp](https://github.com/patarapolw/HanziLevelUp) - A Hanzi learning suite, with levels based on Hanzi Level Project, aka. another attempt to clone WaniKani.com for Chinese. SRS-enabled.
