# anki-export

Export your Anki \*.apkg to Python. Read Anki \*.apkg in Python.

## Example

```python
from anki_export import ApkgReader
import pyexcel_xlsxwx

with ApkgReader('test.apkg') as apkg:
    pyexcel_xlsxwx.save_data('test.xlsx', apkg.export(), config={'format': None})
```

## Installation

```commandline
$ pip install anki-export
```

## Why?

- \*.apkg is quite well structured, convincing me to use this format more.
- Allow you to use \*.apkg programmatically in Python.
- Might be less buggy than https://github.com/patarapolw/AnkiTools
