"""
Dashboard Routes

Handles:
- Public landing page
- Main dashboard
- Records
- Analytics
- Reports
"""

import json
import os

from flask import render_template, request
from flask_login import login_required

from dashboard import dashboard_bp
from extensions import db
from models import VerbalAutopsy
from resources.utils.dashboard_statistics import get_dashboard_statistics


# ==========================================================
# Geographic Reference Data
# ==========================================================

def load_geographic_data():
    """Load Nigerian states and LGA reference data."""

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    resources_dir = os.path.join(base_dir, "resources", "raw")

    states_file = os.path.join(resources_dir, "states.json")
    lgas_file = os.path.join(resources_dir, "lgas.json")

    states = []
    all_lgas = {}

    try:
        with open(states_file, "r", encoding="utf-8") as file:
            states = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        states = []

    try:
        with open(lgas_file, "r", encoding="utf-8") as file:
            all_lgas = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        all_lgas = {}

    return states, all_lgas


# ==========================================================
# Public Landing Page
# ==========================================================

@dashboard_bp.route("/")
def home():
    """Display the public Verbal Autopsy Dashboard landing page."""

    return render_template("landing.html")


# ==========================================================
# Main Dashboard
# ==========================================================

@dashboard_bp.route("/dashboard")
@login_required
def index():
    """Display the authenticated Verbal Autopsy dashboard."""

    statistics = get_dashboard_statistics()

    return render_template(
        "index.html",
        statistics=statistics,
    )


# ==========================================================
# Records
# ==========================================================

@dashboard_bp.route("/records")
@login_required
def records():
    """Display Verbal Autopsy records with filtering and pagination."""

    state = request.args.get("state", "").strip()
    lga = request.args.get("lga", "").strip()
    facility = request.args.get("facility", "").strip()
    sex = request.args.get("sex", "").strip()
    cause = request.args.get("cause", "").strip()
    year = request.args.get("year", "").strip()
    patient = request.args.get("patient", "").strip()

    # ------------------------------------------------------
    # Pagination
    # ------------------------------------------------------

    try:
        page = int(request.args.get("page", 1))
    except (TypeError, ValueError):
        page = 1

    try:
        per_page = int(request.args.get("per_page", 20))
    except (TypeError, ValueError):
        per_page = 20

    page = max(page, 1)
    per_page = min(max(per_page, 10), 100)

    # ------------------------------------------------------
    # Base Query
    # ------------------------------------------------------

    query = VerbalAutopsy.query

    # ------------------------------------------------------
    # Filters
    # ------------------------------------------------------

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
        except (TypeError, ValueError):
            pass

    if patient:
        query = query.filter(
            VerbalAutopsy.patientid.ilike(
                f"%{patient}%"
            )
        )

    # ------------------------------------------------------
    # Pagination
    # ------------------------------------------------------

    pagination = (
        query
        .order_by(VerbalAutopsy.id.desc())
        .paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )
    )

    records_list = pagination.items

    # ------------------------------------------------------
    # Geographic Data
    # ------------------------------------------------------

    states, all_lgas = load_geographic_data()

    lgas = all_lgas.get(state, []) if state else []

    # ------------------------------------------------------
    # Facilities
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # Causes
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # Interview Years
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # Render
    # ------------------------------------------------------

    return render_template(
        "records.html",
        records=records_list,
        pagination=pagination,
        states=states,
        lgas=lgas,
        facilities=facilities,
        causes=causes,
        years=years,
        all_lgas=all_lgas,
    )


# ==========================================================
# Analytics
# ==========================================================

@dashboard_bp.route("/analytics")
@login_required
def analytics():
    """Display dashboard analytics."""

    statistics = get_dashboard_statistics()

    return render_template(
        "Analytics.html",
        statistics=statistics,
    )


# ==========================================================
# Reports
# ==========================================================

@dashboard_bp.route("/reports")
@login_required
def reports():
    """Display dashboard reports."""

    return render_template(
        "reports.html"
    )
