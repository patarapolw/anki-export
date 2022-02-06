import sqlite3
from typing import Any
from zipfile import ZipFile
from tempfile import mkdtemp
import shutil
from collections import OrderedDict
import json
from pathlib import Path


class ApkgReader:
    """Main class for reading *.apkg files."""

    def __init__(
        self,
        apkg_path: str | Path,
        sqlite_path: str | Path = None,
        extract_to: str | Path = None,
    ):
        """Main class for reading *.apkg files.

        Args:
            apkg_path (str | Path): Path to the *.apkg file.
            sqlite_path (str | Path, optional): Path to the actual SQLite file. Defaults to None.
            extract_to (str, optional): Path to the extraction folder. Defaults to `mkdtemp()`.
        """

        self.tempdir = False
        if extract_to:
            Path(extract_to).mkdir(parents=True, exist_ok=True)
            self.extract_to = str(extract_to)
        else:
            self.extract_to = mkdtemp()
            self.tempdir = True

        with ZipFile(str(apkg_path)) as zf:
            zf.extractall(self.extract_to)

        self.sqlite_path = Path(self.extract_to).joinpath("collection.anki21")
        if not self.sqlite_path.exists():
            self.sqlite_path = self.sqlite_path.with_name("collection.anki2")

        if sqlite_path:
            self.sqlite_path.rename(sqlite_path)

        self.conn = sqlite3.connect(str(self.sqlite_path))
        self.conn.row_factory = sqlite3.Row

        self.models = None
        self.decks = None

        cursor = self.conn.execute("SELECT * FROM col")
        col = next(cursor)
        self.models: dict[str, Any] = json.loads(col["models"])
        self.decks: dict[str, Any] = json.loads(col["decks"])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __next__(self):
        return self

    def __iter__(self):
        return self.notes

    def close(self):
        """Close the database connection and clean up"""

        self.conn.close()

        if self.tempdir:
            shutil.rmtree(self.extract_to)

    def find_model_by_id(self, mid):
        """Find model by ID"""

        return self.models.get(str(mid), None)

    def find_deck_by_id(self, did):
        """Find deck by ID"""

        return self.decks.get(str(did), None)

    def find_note_by_id(self, nid):
        """Find note by ID"""

        cursor = self.conn.execute("SELECT * FROM notes WHERE id=?", (nid,))
        return self._format_note(next(cursor))

    @property
    def notes(self):
        """Generate an iterator of notes

        Yields:
            OrderedDict: dictionary of notes
        """

        for note in self.conn.execute("SELECT * FROM notes"):
            yield self._format_note(note)

    def _format_note(self, row):
        note = OrderedDict(row)
        header = self._model_to_header(self.find_model_by_id(note["mid"]))
        note.update(
            {"data": {"record": OrderedDict(zip(header, note["flds"].split("\x1f")))}}
        )

        return note

    @staticmethod
    def _model_to_header(model):
        return [x["name"] for x in sorted(model["flds"], key=lambda x: x["ord"])]

    def find_card_by_id(self, cid):
        """Find card by ID"""

        cursor = self.conn.execute("SELECT * FROM cards WHERE id=?", (cid,))
        return self._format_card(next(cursor))

    @property
    def cards(self):
        """Generate an iterator of cards

        Yields:
            OrderedDict: dictionary of cards
        """

        for card in self.conn.execute("SELECT * FROM cards"):
            yield self._format_card(card)

    def _format_card(self, row):
        card = OrderedDict(row)
        card.update(
            {
                "data": {
                    "note": self.find_note_by_id(card["nid"]),
                    "deck": self.find_deck_by_id(card["did"]),
                }
            }
        )

        return card

    def cards_by_ord(self, ord=0):
        """Get card by ord (position in Note Type)

        Args:
            ord (int, optional): position in Note Type. Defaults to 0.

        Yields:
            OrderedDict: dictionary of cards
        """

        for formatted_card in self.cards:
            if formatted_card["ord"] == ord:
                yield formatted_card

    def export(self, has_header=True, has_deck=True, ords: list[int] = [0]):
        """Export for pyexcel_xlsxwx (OrderedDict of 2-D Lists)

        Args:
            has_header (bool, optional): Whether to add header on the first row. Defaults to True.
            has_deck (bool, optional): Whether to add deck names to the output Defaults to True.
            ords (list[int], optional): positions in Note Type. Defaults to [0].

        Returns:
            OrderedDict: a suitable format for pyexcel_xlsxwx
        """

        result: dict[str, list[list[str]]] = OrderedDict()

        if has_header:
            for model in self.models.values():
                header = list()
                header.extend(self._model_to_header(model))
                header.append("tags")

                if has_deck:
                    header.append("deck")

                result[model["name"]] = [header]

        for ord in ords:
            for formatted_card in self.cards_by_ord(ord=ord):
                record = list()
                record.extend(formatted_card["data"]["note"]["flds"].split("\x1f"))
                record.append(formatted_card["data"]["note"]["tags"])

                if has_deck:
                    record.append(self.find_deck_by_id(formatted_card["did"])["name"])

                result[
                    self.find_model_by_id(formatted_card["data"]["note"]["mid"])["name"]
                ].append(record)

        to_be_del = []
        for k, v in result.items():
            if len(v) == 1:
                to_be_del.append(k)

        for k in to_be_del:
            del result[k]

        return result
