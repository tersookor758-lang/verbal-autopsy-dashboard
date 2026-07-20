from flask_restx import reqparse
from werkzeug.datastructures import FileStorage


upload_parser = reqparse.RequestParser()

upload_parser.add_argument(
    "file",
    location="files",
    type=FileStorage,
    required=True,
    help="Upload a CSV, Excel (.xlsx/.xls), or JSON file."
)