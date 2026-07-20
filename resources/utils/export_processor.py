import io
import json

import pandas as pd


def export_to_csv(records):
    """
    Export records to CSV.

    Returns:
        io.BytesIO
    """

    data = [
        record.to_dict()
        for record in records
    ]

    dataframe = pd.DataFrame(data)

    output = io.BytesIO()

    dataframe.to_csv(
        output,
        index=False
    )

    output.seek(0)

    return output


def export_to_excel(records):
    """
    Export records to Excel (.xlsx).

    Returns:
        io.BytesIO
    """

    data = [
        record.to_dict()
        for record in records
    ]

    dataframe = pd.DataFrame(data)

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        dataframe.to_excel(
            writer,
            index=False,
            sheet_name="Verbal Autopsy"
        )

    output.seek(0)

    return output


def export_to_json(records):
    """
    Export records to JSON.

    Returns:
        io.BytesIO
    """

    data = [
        record.to_dict()
        for record in records
    ]

    output = io.BytesIO()

    output.write(
        json.dumps(
            data,
            indent=4
        ).encode("utf-8")
    )

    output.seek(0)

    return output


def export_records(records, file_type):
    """
    Export records based on requested format.

    Supported formats:
        csv
        excel
        json
    """

    file_type = file_type.lower()

    if file_type == "csv":

        return export_to_csv(records)

    if file_type == "excel":

        return export_to_excel(records)

    if file_type == "json":

        return export_to_json(records)

    raise ValueError(
        "Unsupported export format."
    )