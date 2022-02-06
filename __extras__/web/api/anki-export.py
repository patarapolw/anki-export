import os
from pathlib import Path
from threading import Thread
import atexit
from time import sleep

from anki_export import ApkgReader
import pyexcel_xlsxwx
from flask import Flask, request, Response, send_from_directory, jsonify

TMP_PREFIX = "tmp_"

app = Flask(__name__)


@app.get("/<path:path>")
def download_file(path: str):
    filename = request.args.get("file")
    format = request.args.get("format")

    if format == "xlsx":
        xlsx_exists = False
        if Path(TMP_PREFIX + filename + ".xlsx").exists():
            xlsx_exists = True
        elif Path(TMP_PREFIX + filename).exists():
            with ApkgReader(TMP_PREFIX + filename) as apkg:
                pyexcel_xlsxwx.save_data(
                    TMP_PREFIX + filename + ".xlsx",
                    apkg.export(),
                    config={"format": None},
                )

            xlsx_exists = True

        if xlsx_exists:
            return send_from_directory(
                os.getcwd(),
                Path(TMP_PREFIX + filename + ".xlsx"),
                as_attachment=True,
                download_name="",
            )
    else:
        if Path(TMP_PREFIX + filename).exists():
            with ApkgReader(TMP_PREFIX + filename) as apkg:
                return jsonify(apkg.export())

    return Response(status=404)


@app.post("/<path:path>")
def upload_file(path: str):
    file = request.files["file"]
    filename = file.filename
    format = request.form["format"]

    file.save(TMP_PREFIX + filename)

    Thread(target=lambda: sleep(30) or clear_tmp(filename), daemon=True).start()

    with ApkgReader(TMP_PREFIX + filename) as apkg:
        if format == "xlsx":
            pyexcel_xlsxwx.save_data(
                TMP_PREFIX + filename + ".xlsx",
                apkg.export(),
                config={"format": None},
            )

    return Response(status=201)


def clear_tmp(f: str = ""):
    for p in Path().glob(TMP_PREFIX + f + "*"):
        if p.is_file():
            p.unlink()


atexit.register(clear_tmp)

if __name__ == "__main__":
    app.run(port=9000, debug=True)
