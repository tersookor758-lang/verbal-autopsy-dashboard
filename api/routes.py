from pathlib import Path
import json

from flask import current_app, request, send_file
from flask_restx import Namespace, Resource

from api.api import api
from api.models import (
    verbal_autopsy_model,
    upload_response,
)
from api.parsers import upload_parser
from api.rbac import role_required

from extensions import db
from models import VerbalAutopsy

from resources.utils.upload_processor import process_upload
from resources.utils.export_processor import export_records


BASE_DIR = Path(__file__).resolve().parent.parent

STATES_FILE = BASE_DIR / "resources" / "raw" / "states.json"
LGAS_FILE = BASE_DIR / "resources" / "raw" / "lgas.json"


def load_states():
    """Load the Nigerian states list."""

    with open(STATES_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def load_lgas():
    """Load the state-to-LGA mapping."""

    with open(LGAS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


verbal_autopsy_ns = Namespace(
    "verbal-autopsy",
    description="Operations for Verbal Autopsy records",
)

api.add_namespace(
    verbal_autopsy_ns,
    path="/verbal-autopsy",
)


# ==========================================================
# Location Lookup
# ==========================================================

@verbal_autopsy_ns.route("/locations")
class Locations(Resource):

    # All authenticated users can use location filters.
    @role_required("admin", "upload_user", "user")
    def get(self):

        state = request.args.get("state", "").strip()

        if state:
            return {
                "state": state,
                "lgas": load_lgas().get(state, []),
            }, 200

        return {
            "states": load_states(),
        }, 200


# ==========================================================
# List Records
# ==========================================================

@verbal_autopsy_ns.route("/")
class VerbalAutopsyList(Resource):

    # All authenticated users can view records.
    @role_required("admin", "upload_user", "user")
    @verbal_autopsy_ns.marshal_list_with(verbal_autopsy_model)
    def get(self):

        records = VerbalAutopsy.query.all()

        return [
            record.to_dict()
            for record in records
        ], 200


# ==========================================================
# Single Record Operations
# ==========================================================

@verbal_autopsy_ns.route("/<string:patientid>")
class VerbalAutopsyDetail(Resource):

    # All authenticated users can view a record.
    @role_required("admin", "upload_user", "user")
    @verbal_autopsy_ns.marshal_with(verbal_autopsy_model)
    def get(self, patientid):

        record = VerbalAutopsy.query.filter_by(
            patientid=patientid
        ).first()

        if not record:
            return {
                "message": "Record not found"
            }, 404

        return record.to_dict(), 200

    # Only administrators can edit records.
    @role_required("admin")
    @verbal_autopsy_ns.expect(verbal_autopsy_model)
    @verbal_autopsy_ns.marshal_with(verbal_autopsy_model)
    def put(self, patientid):

        record = VerbalAutopsy.query.filter_by(
            patientid=patientid
        ).first()

        if not record:
            return {
                "message": "Record not found"
            }, 404

        allowed_fields = {
            "state_name",
            "lga_name",
            "facility_name",
            "age",
            "sex",
            "cause_of_death",
            "cause_list",
            "icd10",
            "interviewer_name",
            "interview_year",
            "interview_month",
            "interview_day",
            "interview_time",
        }

        data = request.json or {}

        try:

            for key, value in data.items():

                if key in allowed_fields:
                    setattr(record, key, value)

            db.session.commit()

        except Exception as error:

            db.session.rollback()

            current_app.logger.exception(error)

            return {
                "message": "Failed to update record"
            }, 500

        return record.to_dict(), 200

    # Only administrators can delete records.
    @role_required("admin")
    def delete(self, patientid):

        record = VerbalAutopsy.query.filter_by(
            patientid=patientid
        ).first()

        if not record:
            return {
                "message": "Record not found"
            }, 404

        db.session.delete(record)
        db.session.commit()

        return {
            "message": "Record deleted successfully"
        }, 200


# ==========================================================
# Upload
# ==========================================================

@verbal_autopsy_ns.route("/upload")
class UploadRecords(Resource):

    # Upload is available only to users granted the
    # upload_user role and to administrators.
    @role_required("admin", "upload_user")
    @verbal_autopsy_ns.expect(upload_parser)
    @verbal_autopsy_ns.response(
        200,
        "Upload completed successfully",
        upload_response,
    )
    def post(self):

        uploaded_file = request.files.get("file")

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

        filename = (
            uploaded_file.filename or ""
        ).lower()

        extension = "." + filename.split(".")[-1]

        if extension not in allowed_extensions:
            return {
                "message":
                "Unsupported file format. "
                "Upload CSV, Excel or JSON."
            }, 400

        try:

            result = process_upload(
                uploaded_file
            )

            db.session.commit()

            return {
                "message":
                "Upload completed successfully",
                "summary": result,
            }, 200

        except ValueError as error:

            db.session.rollback()

            return {
                "message": str(error)
            }, 400

        except Exception as error:

            db.session.rollback()

            current_app.logger.exception(error)

            return {
                "message":
                "Upload failed. "
                "Please check your file and try again."
            }, 500


# ==========================================================
# Export
# ==========================================================

@verbal_autopsy_ns.route("/export/<string:file_type>")
class ExportRecords(Resource):

    # All authenticated users can export records.
    @role_required("admin", "upload_user", "user")
    def get(self, file_type):

        file_type = file_type.lower()

        # Only these export formats are supported.
        download_names = {
            "csv": "verbal_autopsy.csv",
            "excel": "verbal_autopsy.xlsx",
            "json": "verbal_autopsy.json",
        }

        mime_types = {
            "csv": "text/csv",
            "excel":
                "application/"
                "vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet",
            "json": "application/json",
        }

        if file_type not in download_names:
            return {
                "message":
                "Unsupported export format. "
                "Use csv, excel or json."
            }, 400

        try:

            exported_file = export_records(
                VerbalAutopsy.query.order_by(
                    VerbalAutopsy.id
                ).all(),
                file_type,
            )

        except ValueError as error:

            return {
                "message": str(error)
            }, 400

        return send_file(
            exported_file,
            as_attachment=True,
            download_name=download_names[file_type],
            mimetype=mime_types[file_type],
        )