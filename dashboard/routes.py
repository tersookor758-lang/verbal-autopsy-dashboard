"""
Dashboard Routes

Handles:
- Main dashboard
- Records
- Analytics
- Reports
"""

from flask import render_template

from flask_login import login_required

from dashboard import dashboard_bp
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
    Display Verbal Autopsy records.
    """

    return render_template(
        "records.html"
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