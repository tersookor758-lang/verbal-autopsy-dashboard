"""
Dashboard Routes

Handles:
- Main dashboard
- Records
- Analytics
- Reports
- Administrator user management
"""

import json
import os

from flask import (
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from flask_login import (
    current_user,
    login_required,
)

from dashboard import dashboard_bp
from extensions import db
from models import (
    User,
    VerbalAutopsy,
)

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
    Display Verbal Autopsy records with filtering
    and pagination.
    """

    # ------------------------------------------------------
    # Query parameters
    # ------------------------------------------------------

    state = request.args.get(
        "state",
        ""
    ).strip()

    lga = request.args.get(
        "lga",
        ""
    ).strip()

    facility = request.args.get(
        "facility",
        ""
    ).strip()

    sex = request.args.get(
        "sex",
        ""
    ).strip()

    cause = request.args.get(
        "cause",
        ""
    ).strip()

    year = request.args.get(
        "year",
        ""
    ).strip()

    patient = request.args.get(
        "patient",
        ""
    ).strip()

    # ------------------------------------------------------
    # Pagination
    # ------------------------------------------------------

    try:
        page = int(
            request.args.get(
                "page",
                1
            )
        )
    except (TypeError, ValueError):
        page = 1

    try:
        per_page = int(
            request.args.get(
                "per_page",
                20
            )
        )
    except (TypeError, ValueError):
        per_page = 20

    page = max(
        page,
        1
    )

    per_page = min(
        max(per_page, 10),
        100
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
    # States
    # ------------------------------------------------------

    states = [
        value[0]
        for value in (
            db.session.query(
                VerbalAutopsy.state_name
            )
            .filter(
                VerbalAutopsy.state_name.isnot(None)
            )
            .filter(
                VerbalAutopsy.state_name != ""
            )
            .distinct()
            .order_by(
                VerbalAutopsy.state_name
            )
            .all()
        )
    ]

    # ------------------------------------------------------
    # LGAs
    # ------------------------------------------------------

    lga_query = db.session.query(
        VerbalAutopsy.lga_name
    ).filter(
        VerbalAutopsy.lga_name.isnot(None)
    ).filter(
        VerbalAutopsy.lga_name != ""
    )

    if state:
        lga_query = lga_query.filter(
            VerbalAutopsy.state_name == state
        )

    lgas = [
        value[0]
        for value in (
            lga_query
            .distinct()
            .order_by(
                VerbalAutopsy.lga_name
            )
            .all()
        )
    ]

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
    # State -> LGA mapping
    # ------------------------------------------------------

    all_lgas = {}

    lga_file = os.path.join(
        os.path.dirname(
            os.path.dirname(__file__)
        ),
        "resources",
        "raw",
        "lgas.json",
    )

    try:

        with open(
            lga_file,
            "r",
            encoding="utf-8",
        ) as file:

            all_lgas = json.load(file)

    except (
        FileNotFoundError,
        json.JSONDecodeError,
    ):

        all_lgas = {}

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


# ==========================================================
# Administrator - User Management
# ==========================================================

@dashboard_bp.route("/admin/users")
@login_required
def admin_users():
    """
    Display the administrator user-management page.

    Only administrators are allowed to access this page.
    """

    if not current_user.is_admin():
        flash(
            "You do not have permission to access "
            "user management.",
            "danger"
        )

        return redirect(
            url_for("dashboard.index")
        )

    users = User.query.order_by(
        User.created_at.desc()
    ).all()

    return render_template(
        "admin_users.html",
        users=users,
    )


# ==========================================================
# Administrator - Approve User
# ==========================================================

@dashboard_bp.route(
    "/admin/users/<int:user_id>/approve",
    methods=["POST"]
)
@login_required
def approve_user(user_id):
    """
    Approve a user account.
    """

    if not current_user.is_admin():
        flash(
            "You do not have permission to perform "
            "this action.",
            "danger"
        )

        return redirect(
            url_for("dashboard.index")
        )

    user = User.query.get_or_404(
        user_id
    )

    user.is_verified = True
    user.is_active = True

    db.session.commit()

    flash(
        f"User '{user.username}' has been approved.",
        "success"
    )

    return redirect(
        url_for("dashboard.admin_users")
    )


# ==========================================================
# Administrator - Activate / Deactivate
# ==========================================================

@dashboard_bp.route(
    "/admin/users/<int:user_id>/toggle-active",
    methods=["POST"]
)
@login_required
def toggle_user_active(user_id):
    """
    Activate or deactivate a user account.
    """

    if not current_user.is_admin():
        flash(
            "You do not have permission to perform "
            "this action.",
            "danger"
        )

        return redirect(
            url_for("dashboard.index")
        )

    user = User.query.get_or_404(
        user_id
    )

    # Prevent an administrator from accidentally
    # deactivating their own account.
    if user.id == current_user.id:
        flash(
            "You cannot deactivate your own account.",
            "warning"
        )

        return redirect(
            url_for("dashboard.admin_users")
        )

    user.is_active = not user.is_active

    db.session.commit()

    if user.is_active:

        flash(
            f"User '{user.username}' has been activated.",
            "success"
        )

    else:

        flash(
            f"User '{user.username}' has been deactivated.",
            "warning"
        )

    return redirect(
        url_for("dashboard.admin_users")
    )


# ==========================================================
# Administrator - Change Role
# ==========================================================

@dashboard_bp.route(
    "/admin/users/<int:user_id>/role",
    methods=["POST"]
)
@login_required
def change_user_role(user_id):
    """
    Change a user's role.

    Allowed roles:
        user
        upload_user
        admin
    """

    if not current_user.is_admin():
        flash(
            "You do not have permission to perform "
            "this action.",
            "danger"
        )

        return redirect(
            url_for("dashboard.index")
        )

    user = User.query.get_or_404(
        user_id
    )

    # Prevent an administrator from changing
    # their own role accidentally.
    if user.id == current_user.id:

        flash(
            "You cannot change your own administrator role.",
            "warning"
        )

        return redirect(
            url_for("dashboard.admin_users")
        )

    new_role = (
        request.form.get(
            "role",
            ""
        )
        .strip()
        .lower()
    )

    allowed_roles = {
        "user",
        "upload_user",
        "admin",
    }

    if new_role not in allowed_roles:

        flash(
            "Invalid role selected.",
            "danger"
        )

        return redirect(
            url_for("dashboard.admin_users")
        )

    user.role = new_role

    db.session.commit()

    flash(
        f"Role for '{user.username}' changed to "
        f"'{new_role}'.",
        "success"
    )

    return redirect(
        url_for("dashboard.admin_users")
    )