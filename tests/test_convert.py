import pytest
from pathlib import Path

import pyexcel_xlsxwx

from anki_export import ApkgReader


@pytest.mark.parametrize("in_file", ["jp-idiom.apkg"])
def test_json(in_file):
    with ApkgReader(str(Path("tests/input").joinpath(in_file))) as apkg:
        output = apkg.export()
        assert len(output["Jap phrase write"]) == 162
        assert all((len(it) == 10) for it in output["Jap phrase write"])
        assert output["Jap phrase write"][0][-2] == "tags"
        assert output["Jap phrase write"][0][-1] == "deck"


@pytest.mark.parametrize("in_file", ["jp-idiom.apkg"])
def test_xlsx(in_file, request):
    with ApkgReader(str(Path("tests/input").joinpath(in_file))) as apkg:
        out_file = Path("tests/output").joinpath(request.node.name).with_suffix(".xlsx")
        if out_file.exists():
            out_file.unlink()

        pyexcel_xlsxwx.save_data(str(out_file), apkg.export(), config={"format": None})
        assert out_file.exists()
