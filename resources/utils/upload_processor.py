import json
import os

import pandas as pd
from flask import current_app

from extensions import db
from models import VerbalAutopsy

from resources.utils.location_normalizer import (
    normalize_state,
    normalize_lga
)

from resources.utils.validators import validate_record


class UploadProcessor:
    """
    Handles importing verbal autopsy records from external files.

    Supported formats:
    - CSV
    - Excel (.xlsx/.xls)
    - JSON

    Responsibilities:
    - Clean incoming data
    - Normalize locations
    - Validate records
    - Insert new patients
    - Update existing patients
    - Return upload statistics
    """

    def __init__(self):
        self.allowed_fields = {
            column.name
            for column in VerbalAutopsy.__table__.columns
        }

    def process_file(self, file_storage):

        filename = file_storage.filename or ""

        extension = os.path.splitext(filename)[1].lower()

        if extension == ".csv":

            try:

                dataframe = pd.read_csv(
                    file_storage,
                    encoding="utf-8"
                )

            except UnicodeDecodeError:

                file_storage.seek(0)

                dataframe = pd.read_csv(
                    file_storage,
                    encoding="latin-1"
                )

        elif extension in [".xlsx", ".xls"]:

            dataframe = pd.read_excel(
                file_storage
            )

        elif extension == ".json":

            data = json.load(
                file_storage
            )

            if isinstance(data, dict):

                if "data" in data:

                    data = data["data"]

                else:

                    data = [data]

            dataframe = pd.DataFrame(data)

        else:

            raise ValueError(
                "Unsupported file format. Use CSV, Excel or JSON."
            )

        return self.process_dataframe(dataframe)

    def process_dataframe(self, dataframe):

        dataframe = dataframe.fillna("")

        summary = {
            "total_rows": len(dataframe),
            "inserted": 0,
            "updated": 0,
            "duplicates": 0,
            "invalid": 0,
            "errors": []
        }

        uploaded_patient_ids = set()

        for row_number, row in enumerate(
            dataframe.to_dict(orient="records"),
            start=2
        ):

            record_data = self.clean_record(row)

            patientid = record_data.get(
                "patientid",
                ""
            )

            if patientid in uploaded_patient_ids:

                summary["duplicates"] += 1

                summary["errors"].append({
                    "row": row_number,
                    "patientid": patientid,
                    "errors": [
                        "Duplicate patient ID found inside uploaded file."
                    ]
                })

                continue

            uploaded_patient_ids.add(patientid)

            validation_errors = validate_record(
                record_data
            )

            if validation_errors:

                summary["invalid"] += 1

                summary["errors"].append({
                    "row": row_number,
                    "patientid": patientid,
                    "errors": validation_errors
                })

                continue

            try:

                filtered_data = {
                    key: value
                    for key, value in record_data.items()
                    if key in self.allowed_fields
                }

                existing_record = VerbalAutopsy.query.filter_by(
                    patientid=patientid
                ).first()

                if existing_record:

                    self.update_record(
                        existing_record,
                        filtered_data
                    )

                    summary["updated"] += 1

                else:

                    new_record = VerbalAutopsy(
                        **filtered_data
                    )

                    db.session.add(new_record)

                    summary["inserted"] += 1

            except Exception as error:

                current_app.logger.exception(error)

                summary["invalid"] += 1

                summary["errors"].append({
                    "row": row_number,
                    "patientid": patientid,
                    "errors": [str(error)]
                })

        db.session.commit()

        return summary

    def clean_record(self, row):

        cleaned = {}

        for key, value in row.items():

            key = str(key).strip().lower()
            key = key.replace(" ", "_")

            cleaned[key] = value

        if "patient_id" in cleaned:

            cleaned["patientid"] = cleaned.pop(
                "patient_id"
            )

        if "state" in cleaned:

            cleaned["state_name"] = cleaned.pop(
                "state"
            )

        if "lga" in cleaned:

            cleaned["lga_name"] = cleaned.pop(
                "lga"
            )

        if "state_name" in cleaned:

            cleaned["state_name"] = normalize_state(
                cleaned["state_name"]
            )

        if "lga_name" in cleaned:

            cleaned["lga_name"] = normalize_lga(
                cleaned["lga_name"]
            )

        return cleaned

    def update_record(self, record, values):

        for key, value in values.items():

            if (
                key in self.allowed_fields
                and hasattr(record, key)
            ):

                setattr(
                    record,
                    key,
                    value
                )


def process_upload(file_storage):

    processor = UploadProcessor()

    return processor.process_file(file_storage)