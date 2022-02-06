import pyexcel_xlsxwx

from anki_export import ApkgReader

with ApkgReader("../../tests/input/jp-idiom.apkg") as apkg:
    pyexcel_xlsxwx.save_data(
        "../../tests/output/jp-idiom.xlsx", apkg.export(), config={"format": None}
    )
