from flask_restx import Api

from api import api_bp


api = Api(
    api_bp,
    version="1.0",
    title="Verbal Autopsy Outcome Dashboard API",
    description="REST API for managing Verbal Autopsy Outcome records.",
    doc="/docs",
    ordered=True
)