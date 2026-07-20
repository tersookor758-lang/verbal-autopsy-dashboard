from pathlib import Path
import json

from flask import request, current_app, send_file
from flask_restx import Namespace, Resource

from api.api import api
from api.models import verbal_autopsy_model
from api.parsers import upload_parser

from extensions import db
from models import VerbalAutopsy

from resources.utils.upload_processor import process_upload
from resources.utils.export_processor import export_records


BASE_DIR = Path(__file__).resolve().parent.parent

STATES_FILE = BASE_DIR / "resources" / "raw" / "states.json"
LGAS_FILE = BASE_DIR / "resources" / "raw" / "lgas.json"


def load_states():

    with open(STATES_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def load_lgas():

    with open(LGAS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


verbal_autopsy_ns = Namespace(
    "verbal-autopsy",
    description="Verbal Autopsy Record Operations"
)

api.add_namespace(
    verbal_autopsy_ns,
    path="/verbal-autopsy"
)


@verbal_autopsy_ns.route("/locations")
class Locations(Resource):

    @verbal_autopsy_ns.doc(
        description="Retrieve Nigerian states or LGAs"
    )
    def get(self):

        state = request.args.get(
            "state",
            ""
        ).strip()

        if state:

            return {
                "state": state,
                "lgas": load_lgas().get(
                    state,
                    []
                )
            }, 200

        return {
            "states": load_states()
        }, 200


# ------------------------------------------------------------------
# Existing endpoints below (keep the rest of your file exactly as-is)
# ------------------------------------------------------------------

@verbal_autopsy_ns.route("/")
class VerbalAutopsyList(Resource):

    @verbal_autopsy_ns.doc(
        description="Retrieve all verbal autopsy records"
    )
    def get(self):

        records = VerbalAutopsy.query.all()

        return [

            record.to_dict()

            for record in records

        ], 200


@verbal_autopsy_ns.route("/<string:patientid>")
class VerbalAutopsyDetail(Resource):

    @verbal_autopsy_ns.doc(
        description="Retrieve a single record by patient ID"
    )
    def get(
        self,
        patientid
    ):

        record = VerbalAutopsy.query.filter_by(
            patientid=patientid
        ).first()

        if not record:

            return {

                "message": "Record not found"

            }, 404

        return record.to_dict(), 200

    @verbal_autopsy_ns.expect(
        verbal_autopsy_model
    )
    @verbal_autopsy_ns.doc(
        description="Update an existing record"
    )
    def put(
        self,
        patientid
    ):

        record = VerbalAutopsy.query.filter_by(
            patientid=patientid
        ).first()

        if not record:

            return {

                "message": "Record not found"

            }, 404

        data = request.json

        for key, value in data.items():

            if hasattr(
                record,
                key
            ):

                setattr(
                    record,
                    key,
                    value
                )

        db.session.commit()

        return record.to_dict(), 200

    @verbal_autopsy_ns.doc(
        description="Delete a record"
    )
    def delete(
        self,
        patientid
    ):

        record = VerbalAutopsy.query.filter_by(
            patientid=patientid
        ).first()

        if not record:

            return {

                "message": "Record not found"

            }, 404

        db.session.delete(
            record
        )

        db.session.commit()

        return {

            "message": "Record deleted successfully"

        }, 200


@verbal_autopsy_ns.route("/upload")
class UploadRecords(Resource):

    @verbal_autopsy_ns.expect(
        upload_parser
    )
    @verbal_autopsy_ns.doc(
        description="Upload CSV, Excel or JSON records and validate them"
    )
    def post(
        self
    ):

        uploaded_file = request.files.get(
            "file"
        )

        if not uploaded_file:

            return {

                "message": "No file uploaded"

            }, 400

        allowed_extensions = {

            "." + extension

            for extension in current_app.config[
                "ALLOWED_UPLOAD_EXTENSIONS"
            ]

        }

        filename = uploaded_file.filename.lower()

        extension = "." + filename.split(".")[-1]

        if extension not in allowed_extensions:

            return {

                "message": "Unsupported file format. Upload CSV, Excel or JSON."

            }, 400

        try:

            result = process_upload(
                uploaded_file
            )

            return {

                "message": "Upload completed successfully",

                "summary": result

            }, 200

        except ValueError as error:

            return {

                "message": str(error)

            }, 400

        except Exception as error:

            current_app.logger.exception(
                error
            )

            return {

                "message": "Upload failed. Please check your file and try again."

            }, 500


@verbal_autopsy_ns.route("/export/<string:file_type>")
class ExportRecords(Resource):

    @verbal_autopsy_ns.doc(
        description="Export all Verbal Autopsy records"
    )
    def get(
        self,
        file_type
    ):

        try:

            exported_file = export_records(

                VerbalAutopsy.query.order_by(
                    VerbalAutopsy.id
                ).all(),

                file_type

            )

        except ValueError as error:

            return {

                "message": str(error)

            }, 400

        download_names = {

            "csv": "verbal_autopsy.csv",

            "excel": "verbal_autopsy.xlsx",

            "json": "verbal_autopsy.json"

        }

        mime_types = {

            "csv": "text/csv",

            "excel": (
                "application/vnd.openxmlformats-"
                "officedocument.spreadsheetml.sheet"
            ),

            "json": "application/json"

        }

        return send_file(

            exported_file,

            as_attachment=True,

            download_name=download_names[
                file_type.lower()
            ],

            mimetype=mime_types[
                file_type.lower()
            ]

        )