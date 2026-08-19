"""
Dashboard Routes

Handles:
- Main dashboard
- Records
- Analytics
- Reports
"""

import json
import os

from flask import (
    render_template,
    request,
)

from flask_login import login_required

from dashboard import dashboard_bp
from extensions import db
from models import VerbalAutopsy

from resources.utils.dashboard_statistics import (
    get_dashboard_statistics,
)


# ==========================================================
# Geographic Reference Data
# ==========================================================

def load_geographic_data():
    """
    Load the complete Nigerian state and LGA reference data.

    Geographic filter options come from the reference JSON files,
    NOT from the states/LGAs currently represented in the database.
    """

    base_dir = os.path.dirname(
        os.path.dirname(__file__)
    )

    resources_dir = os.path.join(
        base_dir,
        "resources",
        "raw",
    )

    states_file = os.path.join(
        resources_dir,
        "states.json",
    )

    lgas_file = os.path.join(
        resources_dir,
        "lgas.json",
    )

    states = []
    all_lgas = {}

    # ------------------------------------------------------
    # States
    # ------------------------------------------------------

    try:
        with open(
            states_file,
            "r",
            encoding="utf-8",
        ) as file:
            states = json.load(file)

    except (
        FileNotFoundError,
        json.JSONDecodeError,
    ):
        states = []

    # ------------------------------------------------------
    # LGAs
    # ------------------------------------------------------

    try:
        with open(
            lgas_file,
            "r",
            encoding="utf-8",
        ) as file:
            all_lgas = json.load(file)

    except (
        FileNotFoundError,
        json.JSONDecodeError,
    ):
        all_lgas = {}

    return states, all_lgas


# ==========================================================
# Main Dashboard
# ==========================================================

@dashboard_bp.route("/")
@login_required
def index():
    """
    Display the main Verbal Autopsy dashboard.
    """

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
    """
    Display Verbal Autopsy records with filtering
    and pagination.
    """

    # ------------------------------------------------------
    # Query parameters
    # ------------------------------------------------------

    state = request.args.get(
        "state",
        "",
    ).strip()

    lga = request.args.get(
        "lga",
        "",
    ).strip()

    facility = request.args.get(
        "facility",
        "",
    ).strip()

    sex = request.args.get(
        "sex",
        "",
    ).strip()

    cause = request.args.get(
        "cause",
        "",
    ).strip()

    year = request.args.get(
        "year",
        "",
    ).strip()

    patient = request.args.get(
        "patient",
        "",
    ).strip()

    # ------------------------------------------------------
    # Pagination
    # ------------------------------------------------------

    try:
        page = int(
            request.args.get(
                "page",
                1,
            )
        )
    except (TypeError, ValueError):
        page = 1

    try:
        per_page = int(
            request.args.get(
                "per_page",
                20,
            )
        )
    except (TypeError, ValueError):
        per_page = 20

    page = max(
        page,
        1,
    )

    per_page = min(
        max(per_page, 10),
        100,
    )

    # ------------------------------------------------------
    # Base query
    # ------------------------------------------------------

    query = VerbalAutopsy.query

    # ------------------------------------------------------
    # Apply filters
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
        except ValueError:
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

    pagination = query.order_by(
        VerbalAutopsy.id.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )

    records = pagination.items

    # ------------------------------------------------------
    # Geographic Reference Data
    # ------------------------------------------------------
    #
    # IMPORTANT:
    #
    # States and LGAs are NOT taken from the database.
    #
    # This ensures the filters contain the complete Nigerian
    # geographic reference list even when there are currently
    # no records from a particular state or LGA.
    # ------------------------------------------------------

    states, all_lgas = load_geographic_data()

    # ------------------------------------------------------
    # Selected state's LGAs
    # ------------------------------------------------------
    #
    # When a state is selected, use the complete LGA list
    # belonging to that state.
    #
    # Do NOT restrict this to LGAs with records.
    # ------------------------------------------------------

    lgas = []

    if state:
        lgas = all_lgas.get(
            state,
            [],
        )

    # ------------------------------------------------------
    # Facilities
    # ------------------------------------------------------

    facilities = [
        value[0]
        for value in (
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
        value[0]
        for value in (
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
    # Interview years
    # ------------------------------------------------------

    years = [
        value[0]
        for value in (
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
        records=records,
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
    """
    Display dashboard analytics.
    """

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
    """
    Display dashboard reports.
    """

    return render_template(
        "reports.html"
    )