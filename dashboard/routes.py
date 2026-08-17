"""
Dashboard Routes

Handles:
- Main dashboard
- Records
- Analytics
- Reports
"""

from flask import render_template, request

from flask_login import login_required

from dashboard import dashboard_bp
from models import VerbalAutopsy
from resources.utils.dashboard_statistics import (
    get_dashboard_statistics,
)


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
    Display Verbal Autopsy records with pagination
    and LGA lookup data.
    """

    # ------------------------------------------------------
    # Pagination
    # ------------------------------------------------------

    page = request.args.get(
        "page",
        1,
        type=int,
    )

    per_page = request.args.get(
        "per_page",
        10,
        type=int,
    )

    if page < 1:
        page = 1

    if per_page not in (10, 25, 50, 100):
        per_page = 10

    # ------------------------------------------------------
    # Get records
    # ------------------------------------------------------

    pagination = VerbalAutopsy.query.paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )

    records = pagination.items

    # ------------------------------------------------------
    # Load State -> LGA mapping
    # ------------------------------------------------------

    import json
    from pathlib import Path

    lga_file = (
        Path(__file__).resolve().parent.parent
        / "resources"
        / "raw"
        / "lgas.json"
    )

    all_lgas = {}

    if lga_file.exists():
        try:
            with open(
                lga_file,
                "r",
                encoding="utf-8",
            ) as file:
                all_lgas = json.load(file)

        except (
            json.JSONDecodeError,
            OSError,
        ):
            all_lgas = {}

    # ------------------------------------------------------
    # Render records page
    # ------------------------------------------------------

    return render_template(
        "records.html",
        records=records,
        pagination=pagination,
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