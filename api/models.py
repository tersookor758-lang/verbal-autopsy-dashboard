from flask_restx import fields

from api.api import api


verbal_autopsy_model = api.model(
    "VerbalAutopsy",
    {
        "patientid": fields.String(
            required=True,
            description="Unique Patient ID",
            example="PAT001"
        ),

        "state_name": fields.String(
            description="State Name",
            example="Benue"
        ),

        "lga_name": fields.String(
            description="Local Government Area",
            example="Makurdi"
        ),

        "facility_name": fields.String(
            description="Facility Name",
            example="General Hospital Makurdi"
        ),

        "datim_code": fields.String(
            required=True,
            description="DATIM Code",
            example="NG123456"
        ),

        "age": fields.Integer(
            description="Age",
            example=45
        ),

        "sex": fields.String(
            description="Sex",
            enum=["Male", "Female"],
            example="Male"
        ),

        "cause_of_death": fields.String(
            description="Cause of Death",
            example="Stroke"
        ),

        "cause_list": fields.Integer(
            description="Cause List Identifier",
            example=1
        ),

        "icd10": fields.String(
            description="ICD-10 Code",
            example="I64"
        ),

        "interviewer_name": fields.String(
            description="Interviewer Name",
            example="John Doe"
        ),

        "interview_year": fields.Integer(
            description="Interview Year",
            example=2025
        ),

        "interview_month": fields.String(
            description="Interview Month",
            example="July"
        ),

        "interview_day": fields.Integer(
            description="Interview Day",
            example=13
        ),

        "interview_time": fields.String(
            description="Interview Time",
            example="10:30 AM"
        )
    }
)


statistics_model = api.model(
    "DashboardStatistics",
    {
        "total_records": fields.Integer(
            description="Total number of verbal autopsy records",
            example=500
        ),

        "male_records": fields.Integer(
            description="Number of male records",
            example=280
        ),

        "female_records": fields.Integer(
            description="Number of female records",
            example=220
        ),

        "total_states": fields.Integer(
            description="Number of states represented",
            example=36
        ),

        "total_facilities": fields.Integer(
            description="Number of facilities represented",
            example=120
        )
    }
)


upload_response = api.model(
    "UploadResponse",
    {
        "message": fields.String(
            description="Upload status message",
            example="Upload completed successfully"
        ),

        "summary": fields.Raw(
            description="Upload processing summary"
        )
    }
)


error_model = api.model(
    "ErrorResponse",
    {
        "message": fields.String(
            description="Error message",
            example="Record not found"
        )
    }
)