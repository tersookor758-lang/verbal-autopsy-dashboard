from flask_restx import Api

from api import api_bp


authorizations = {
    "BearerAuth": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": "JWT authorization header. Enter: Bearer <access_token>",
    }
}


api = Api(
    api_bp,

    version="1.0",

    title="Verbal Autopsy Outcome Dashboard API",

    description="""
REST API for the Verbal Autopsy Outcome Dashboard.

This API provides endpoints for:

• Uploading Verbal Autopsy datasets
• Viewing all records
• Viewing a single record
• Updating records
• Deleting records
• Exporting records
• Dashboard statistics
• State and LGA lookup

Built with Flask, Flask-RESTX and MySQL.
""",

    doc="/swagger",

    authorizations=authorizations,

    security="BearerAuth",

    ordered=True,

    contact="JP",

    license="MIT",

    default="Verbal Autopsy",

    default_label="Verbal Autopsy Operations"
)
