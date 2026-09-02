"""
Dashboard Routes
"""

import json
import os

from flask import jsonify, render_template, request, send_file
from flask_login import login_required

from dashboard import dashboard_bp
from extensions import db
from models import VerbalAutopsy
from resources.utils.dashboard_statistics import (
    get_dashboard_statistics,
    get_state_analytics,
)


def load_geographic_data():
    """Load Nigerian states and LGA reference data."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    resources_dir = os.path.join(base_dir, "resources", "raw")

    states = []
    all_lgas = {}

    try:
        with open(
            os.path.join(resources_dir, "states.json"),
            "r",
            encoding="utf-8",
        ) as file:
            states = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    try:
        with open(
            os.path.join(resources_dir, "lgas.json"),
            "r",
            encoding="utf-8",
        ) as file:
            all_lgas = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    return states, all_lgas


@dashboard_bp.route("/")
def home():
    """Display the public landing page."""
    return render_template("landing.html")


@dashboard_bp.route("/data/nigeria-states.geo.json")
def nigeria_geojson():
    """Serve the Nigeria state boundary GeoJSON."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    geojson_path = os.path.join(
        base_dir,
        "resources",
        "raw",
        "nigeria_states.geo.json",
    )

    return send_file(
        geojson_path,
        mimetype="application/geo+json",
        max_age=3600,
        conditional=True,
    )


@dashboard_bp.route("/data/state-summary")
def state_summary():
    """
    Return public aggregate statistics for a Nigerian state.

    This endpoint intentionally exposes only aggregated information.
    It does not return individual Verbal Autopsy records.
    """

    state = request.args.get(
        "state",
        "",
    ).strip()

    if not state:
        return jsonify(
            {
                "message": "State parameter is required."
            }
        ), 400

    try:
        analytics = get_state_analytics(state)

        return jsonify(
            {
                "state": analytics["state"],
                "observed_records": analytics["observed_records"],
                "estimated_records": None,
                "estimated_records_status": (
                    "Not available until a validated "
                    "state-level estimation methodology "
                    "is implemented."
                ),
                "reporting_facilities": analytics[
                    "reporting_facilities"
                ],
                "reporting_lgas": analytics[
                    "reporting_lgas"
                ],
                "top_cause": analytics["top_cause"],
                "top_cause_percentage": analytics[
                    "top_cause_percentage"
                ],
                "male": analytics["male"],
                "female": analytics["female"],
                "latest_year": analytics["latest_year"],
            }
        ), 200

    except Exception:
        return jsonify(
            {
                "message": "Failed to retrieve state summary."
            }
        ), 500


@dashboard_bp.route("/dashboard")
@login_required
def index():
    """Display the authenticated dashboard."""
    return render_template(
        "index.html",
        statistics=get_dashboard_statistics(),
    )


@dashboard_bp.route("/records")
@login_required
def records():
    """Display records with filtering and pagination."""
    state = request.args.get("state", "").strip()
    lga = request.args.get("lga", "").strip()
    facility = request.args.get("facility", "").strip()
    sex = request.args.get("sex", "").strip()
    cause = request.args.get("cause", "").strip()
    year = request.args.get("year", "").strip()
    patient = request.args.get("patient", "").strip()

    try:
        page = max(int(request.args.get("page", 1)), 1)
    except (TypeError, ValueError):
        page = 1

    try:
        per_page = int(request.args.get("per_page", 20))
    except (TypeError, ValueError):
        per_page = 20

    per_page = min(max(per_page, 10), 100)

    query = VerbalAutopsy.query

    if state:
        query = query.filter(
            VerbalAutopsy.state_name == state
        )

    if lga:
        query = query.filter(
            VerbalAutopsy.lga_name == lga
        )

    if facility:
        query = query.filter(
            VerbalAutopsy.facility_name == facility
        )

    if sex:
        query = query.filter(
            VerbalAutopsy.sex == sex
        )

    if cause:
        query = query.filter(
            VerbalAutopsy.cause_of_death == cause
        )

    if year:
        try:
            query = query.filter(
                VerbalAutopsy.interview_year == int(year)
            )
        except ValueError:
            pass

    if patient:
        query = query.filter(
            VerbalAutopsy.patientid.ilike(
                f"%{patient}%"
            )
        )

    pagination = (
        query
        .order_by(VerbalAutopsy.id.desc())
        .paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )
    )

    states, all_lgas = load_geographic_data()
    lgas = all_lgas.get(
        state,
        []
    ) if state else []

    facilities = [
        row[0]
        for row in (
            db.session.query(
                VerbalAutopsy.facility_name
            )
            .filter(
                VerbalAutopsy.facility_name.isnot(None)
            )
            .filter(
                VerbalAutopsy.facility_name != ""
            )
            .distinct()
            .order_by(
                VerbalAutopsy.facility_name
            )
            .all()
        )
    ]

    causes = [
        row[0]
        for row in (
            db.session.query(
                VerbalAutopsy.cause_of_death
            )
            .filter(
                VerbalAutopsy.cause_of_death.isnot(None)
            )
            .filter(
                VerbalAutopsy.cause_of_death != ""
            )
            .distinct()
            .order_by(
                VerbalAutopsy.cause_of_death
            )
            .all()
        )
    ]

    years = [
        row[0]
        for row in (
            db.session.query(
                VerbalAutopsy.interview_year
            )
            .filter(
                VerbalAutopsy.interview_year.isnot(None)
            )
            .distinct()
            .order_by(
                VerbalAutopsy.interview_year.desc()
            )
            .all()
        )
    ]

    return render_template(
        "records.html",
        records=pagination.items,
        pagination=pagination,
        states=states,
        lgas=lgas,
        facilities=facilities,
        causes=causes,
        years=years,
        all_lgas=all_lgas,
    )


@dashboard_bp.route("/analytics")
@login_required
def analytics():
    """Display dashboard analytics."""
    return render_template(
        "Analytics.html",
        statistics=get_dashboard_statistics(),
    )


@dashboard_bp.route("/reports")
@login_required
def reports():
    """Display dashboard reports."""
    return render_template(
        "reports.html"
    )