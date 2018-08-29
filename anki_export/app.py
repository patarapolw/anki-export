import sqlite3
from zipfile import ZipFile
import os
from tempfile import mkdtemp
import shutil
from collections import OrderedDict
import json


class ApkgReader:
    def __init__(self, apkg_path: str):
        self.temp_dir = mkdtemp()
        with ZipFile(apkg_path) as zf:
            zf.extractall(self.temp_dir)
        self.conn = sqlite3.connect(os.path.join(self.temp_dir, 'collection.anki2'))
        self.conn.row_factory = sqlite3.Row

        self.models = None
        self.decks = None
        self.init()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __next__(self):
        return self

    def __iter__(self):
        return self.notes

    def close(self):
        self.conn.close()
        shutil.rmtree(self.temp_dir)

    def init(self):
        cursor = self.conn.execute('SELECT * FROM col')
        col = next(cursor)
        self.models = json.loads(col['models'])
        self.decks = json.loads(col['decks'])

    def find_model_by_id(self, mid):
        return self.models.get(str(mid), None)

    def find_deck_by_id(self, did):
        return self.decks.get(str(did), None)

    def find_note_by_id(self, nid):
        cursor = self.conn.execute('SELECT * FROM notes WHERE id=?', (nid,))
        return self._format_note(next(cursor))

    @property
    def notes(self):
        for note in self.conn.execute('SELECT * FROM notes'):
            yield self._format_note(note)

    def _format_note(self, row):
        note = OrderedDict(row)
        header = self._model_to_header(self.find_model_by_id(note['mid']))
        note.update({
            'data': {
                'record': OrderedDict(zip(header, note['flds'].split('\x1f')))
            }
        })

        return note

    @staticmethod
    def _model_to_header(model):
        return [x['name'] for x in sorted(model['flds'], key=lambda x: x['ord'])]

    def find_card_by_id(self, cid):
        cursor = self.conn.execute('SELECT * FROM cards WHERE id=?', (cid,))
        return self._format_card(next(cursor))

    @property
    def cards(self):
        for card in self.conn.execute('SELECT * FROM cards'):
            yield self._format_card(card)

    def _format_card(self, row):
        card = OrderedDict(row)
        card.update({
            'data': {
                'note': self.find_note_by_id(card['nid']),
                'deck': self.find_deck_by_id(card['did'])
            }
        })

        return card

    def cards_by_ord(self, ord=0):
        for formatted_card in self.cards:
            if formatted_card['ord'] == ord:
                yield formatted_card

    def export(self, has_header=True, has_deck=True, ord=0):
        result = OrderedDict()

        if has_header:
            for model in self.models.values():
                header = list()
                header.extend(self._model_to_header(model))
                header.append('tags')

                if has_deck:
                    header.append('deck')

                result[model['name']] = [header]

        for formatted_card in self.cards_by_ord(ord=ord):
            record = list()
            record.extend(formatted_card['data']['note']['flds'].split('\x1f'))
            record.append(formatted_card['data']['note']['tags'])

            if has_deck:
                record.append(self.find_deck_by_id(formatted_card['did'])['name'])

            result[self.find_model_by_id(formatted_card['data']['note']['mid'])['name']].append(record)

        return result


if __name__ == '__main__':
    import pyexcel_xlsxwx
    from time import time

    start = time()

    with ApkgReader('/Users/patarapolw/PycharmProjects/AnkiTools/tests/input/test.apkg') as apkg:
        pyexcel_xlsxwx.save_data('test.xlsx', apkg.export(), config={'format': None})

    print(time() - start)
