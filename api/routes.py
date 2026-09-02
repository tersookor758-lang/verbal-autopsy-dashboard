from pathlib import Path
import json

from flask import current_app, request, send_file
from flask_restx import Namespace, Resource

from api.api import api
from api.models import verbal_autopsy_model, upload_response
from api.parsers import upload_parser
from api.rbac import role_required
from extensions import db
from models import VerbalAutopsy

from resources.utils.upload_processor import process_upload
from resources.utils.export_processor import export_records
from resources.utils.dashboard_statistics import get_state_analytics


BASE_DIR = Path(__file__).resolve().parent.parent

STATES_FILE = BASE_DIR / "resources" / "raw" / "states.json"
LGAS_FILE = BASE_DIR / "resources" / "raw" / "lgas.json"


def load_states():
    with open(
        STATES_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def load_lgas():
    with open(
        LGAS_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


verbal_autopsy_ns = Namespace(
    "verbal-autopsy",
    description="Operations for Verbal Autopsy records"
)


api.add_namespace(
    verbal_autopsy_ns,
    path="/verbal-autopsy"
)


# ==========================================================
# LOCATION LOOKUP
# ==========================================================

@verbal_autopsy_ns.route("/locations")
class Locations(Resource):

    @role_required("admin", "upload_user", "user")
    @verbal_autopsy_ns.doc(
        description="""
        Retrieve Nigerian geographical information.

        Without a state parameter:
        - Returns all states.

        With a state parameter:
        - Returns all LGAs belonging to that state.
        """
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


# ==========================================================
# STATE ANALYTICS
# ==========================================================

@verbal_autopsy_ns.route("/state-analytics")
class StateAnalytics(Resource):

    @role_required("admin", "upload_user", "user")
    @verbal_autopsy_ns.doc(
        description="""
        Retrieve observed Verbal Autopsy statistics for a
        specific Nigerian state.

        This endpoint reports statistics calculated from the
        application's Verbal Autopsy database.

        It does not represent a WHO-estimated state burden.
        """
    )
    def get(self):
        state = request.args.get(
            "state",
            ""
        ).strip()

        if not state:
            return {
                "message": "State parameter is required."
            }, 400

        try:
            analytics = get_state_analytics(state)

            return analytics, 200

        except Exception as error:
            current_app.logger.exception(
                error
            )

            return {
                "message": "Failed to retrieve state analytics."
            }, 500


# ==========================================================
# LIST RECORDS
# ==========================================================

@verbal_autopsy_ns.route("/")
class VerbalAutopsyList(Resource):

    @role_required("admin", "upload_user", "user")
    @verbal_autopsy_ns.doc(
        description="Retrieve all Verbal Autopsy records"
    )
    @verbal_autopsy_ns.marshal_list_with(
        verbal_autopsy_model
    )
    def get(self):
        records = VerbalAutopsy.query.all()

        return [
            record.to_dict()
            for record in records
        ], 200


# ==========================================================
# SINGLE RECORD OPERATIONS
# ==========================================================

@verbal_autopsy_ns.route("/<string:patientid>")
class VerbalAutopsyDetail(Resource):

    @role_required("admin", "upload_user", "user")
    @verbal_autopsy_ns.doc(
        description="Retrieve a record using patient ID"
    )
    @verbal_autopsy_ns.marshal_with(
        verbal_autopsy_model
    )
    def get(self, patientid):

        record = VerbalAutopsy.query.filter_by(
            patientid=patientid
        ).first()

        if not record:
            return {
                "message": "Record not found"
            }, 404

        return record.to_dict(), 200

    @role_required("admin")
    @verbal_autopsy_ns.expect(
        verbal_autopsy_model
    )
    @verbal_autopsy_ns.marshal_with(
        verbal_autopsy_model
    )
    @verbal_autopsy_ns.doc(
        description="Update an existing Verbal Autopsy record"
    )
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
            "interview_time"
        }

        data = request.json or {}

        if not isinstance(data, dict):
            return {
                "message": "Request body must be a JSON object."
            }, 400

        try:
            for key, value in data.items():
                if key in allowed_fields:
                    setattr(
                        record,
                        key,
                        value
                    )

            db.session.commit()

        except Exception as error:
            db.session.rollback()

            current_app.logger.exception(
                error
            )

            return {
                "message": "Failed to update record"
            }, 500

        return record.to_dict(), 200

    @role_required("admin")
    @verbal_autopsy_ns.doc(
        description="Delete a Verbal Autopsy record"
    )
    def delete(self, patientid):

        record = VerbalAutopsy.query.filter_by(
            patientid=patientid
        ).first()

        if not record:
            return {
                "message": "Record not found"
            }, 404

        try:
            db.session.delete(
                record
            )

            db.session.commit()

        except Exception as error:
            db.session.rollback()

            current_app.logger.exception(
                error
            )

            return {
                "message": "Failed to delete record"
            }, 500

        return {
            "message": "Record deleted successfully"
        }, 200


# ==========================================================
# UPLOAD
# ==========================================================

@verbal_autopsy_ns.route("/upload")
class UploadRecords(Resource):

    @role_required("admin", "upload_user")
    @verbal_autopsy_ns.expect(
        upload_parser
    )
    @verbal_autopsy_ns.response(
        200,
        "Upload completed successfully",
        upload_response
    )
    @verbal_autopsy_ns.doc(
        description="""
        Upload Verbal Autopsy datasets.

        Supported formats:
        - CSV
        - Excel
        - JSON
        """
    )
    def post(self):

        uploaded_file = request.files.get(
            "file"
        )

        if not uploaded_file:
            return {
                "message": "No file uploaded"
            }, 400

        filename = (
            uploaded_file.filename or ""
        ).strip()

        if not filename:
            return {
                "message": "No file selected."
            }, 400

        allowed_extensions = {
            "." + extension.lower().lstrip(".")
            for extension in current_app.config[
                "ALLOWED_UPLOAD_EXTENSIONS"
            ]
        }

        extension = Path(
            filename
        ).suffix.lower()

        if extension not in allowed_extensions:
            return {
                "message":
                "Unsupported file format. Upload CSV, Excel or JSON."
            }, 400

        try:
            result = process_upload(
                uploaded_file
            )

            db.session.commit()

            return {
                "message":
                "Upload completed successfully",
                "summary": result
            }, 200

        except ValueError as error:
            db.session.rollback()

            return {
                "message": str(error)
            }, 400

        except Exception as error:
            db.session.rollback()

            current_app.logger.exception(
                error
            )

            return {
                "message":
                "Upload failed. Please check your file and try again."
            }, 500


# ==========================================================
# EXPORT
# ==========================================================

@verbal_autopsy_ns.route("/export/<string:file_type>")
class ExportRecords(Resource):

    @role_required("admin", "upload_user", "user")
    @verbal_autopsy_ns.doc(
        description="""
        Export all Verbal Autopsy records.

        Supported export formats:
        - csv
        - excel
        - json
        """
    )
    def get(self, file_type):

        file_type = file_type.strip().lower()

        supported_types = {
            "csv",
            "excel",
            "json"
        }

        if file_type not in supported_types:
            return {
                "message":
                "Invalid export format. Use csv, excel or json."
            }, 400

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

        except Exception as error:
            current_app.logger.exception(
                error
            )

            return {
                "message": "Failed to export records."
            }, 500

        download_names = {
            "csv": "verbal_autopsy.csv",
            "excel": "verbal_autopsy.xlsx",
            "json": "verbal_autopsy.json"
        }

        return send_file(
            exported_file,
            as_attachment=True,
            download_name=download_names[file_type]
        )
