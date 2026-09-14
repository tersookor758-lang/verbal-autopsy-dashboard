"""
Administrator routes for the Verbal Autopsy Outcome Dashboard.
"""

from functools import wraps

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from extensions import db
from models import User


admin_bp = Blueprint(
    "admin",
    __name__,
)


SUPER_ADMIN_USERNAME = "admin"

VALID_ROLES = {
    "user",
    "upload_user",
    "admin",
}


def is_super_admin(user):
    """Return True when the user is the permanent Super Administrator."""

    return (
        user is not None
        and user.username.lower() == SUPER_ADMIN_USERNAME
    )


def admin_required(view):
    """Restrict access to active administrator accounts."""

    @wraps(view)
    @login_required
    def wrapped_view(*args, **kwargs):

        if not current_user.is_active:
            flash(
                "Your account is inactive.",
                "danger",
            )
            return redirect(
                url_for("auth.login")
            )

        if not current_user.is_admin():
            flash(
                "Administrator access is required.",
                "danger",
            )
            return redirect(
                url_for("dashboard.index")
            )

        return view(*args, **kwargs)

    return wrapped_view


def protected_target(user):
    """Return True when the target is the permanent Super Administrator."""

    return is_super_admin(user)


@admin_bp.after_request
def add_no_cache_headers(response):
    """Prevent administrator pages from being cached."""

    response.headers["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, max-age=0"
    )

    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


@admin_bp.route("/")
@admin_required
def index():
    """Display the administrator dashboard."""

    total_users = User.query.count()

    verified_users = User.query.filter_by(
        is_verified=True
    ).count()

    pending_users = User.query.filter_by(
        is_verified=False
    ).count()

    active_users = User.query.filter_by(
        is_active=True
    ).count()

    inactive_users = User.query.filter_by(
        is_active=False
    ).count()

    admin_users = User.query.filter_by(
        role="admin"
    ).count()

    regular_users = User.query.filter_by(
        role="user"
    ).count()

    upload_users = User.query.filter_by(
        role="upload_user"
    ).count()

    recent_users = (
        User.query
        .order_by(User.created_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "index.html",
        total_users=total_users,
        verified_users=verified_users,
        pending_users=pending_users,
        active_users=active_users,
        inactive_users=inactive_users,
        admin_users=admin_users,
        regular_users=regular_users,
        upload_users=upload_users,
        recent_users=recent_users,
    )


@admin_bp.route("/users")
@admin_required
def users():
    """
    Display all users for administrator management.

    The user-management page must use an existing project template.
    """

    all_users = (
        User.query
        .order_by(User.created_at.desc())
        .all()
    )

    return render_template(
        "users.html",
        users=all_users,
        super_admin_username=SUPER_ADMIN_USERNAME,
    )


@admin_bp.route("/users/<int:user_id>/verify", methods=["POST"])
@admin_required
def verify_user(user_id):
    """Verify a user account."""

    user = db.session.get(User, user_id)

    if user is None:
        flash(
            "User not found.",
            "danger",
        )
        return redirect(
            url_for("admin.users")
        )

    if protected_target(user):
        flash(
            "The Super Administrator account cannot be modified.",
            "danger",
        )
        return redirect(
            url_for("admin.users")
        )

    try:
        user.is_verified = True

        db.session.commit()

        flash(
            f"User '{user.username}' has been verified.",
            "success",
        )

    except Exception:
        db.session.rollback()

        flash(
            "Unable to verify the user.",
            "danger",
        )

    return redirect(
        url_for("admin.users")
    )


@admin_bp.route("/users/<int:user_id>/unverify", methods=["POST"])
@admin_required
def unverify_user(user_id):
    """Remove verification from a user account."""

    user = db.session.get(User, user_id)

    if user is None:
        flash(
            "User not found.",
            "danger",
        )
        return redirect(
            url_for("admin.users")
        )

    if protected_target(user):
        flash(
            "The Super Administrator account cannot be modified.",
            "danger",
        )
        return redirect(
            url_for("admin.users")
        )

    try:
        user.is_verified = False

        db.session.commit()

        flash(
            f"User '{user.username}' is now unverified.",
            "success",
        )

    except Exception:
        db.session.rollback()

        flash(
            "Unable to change the user's verification status.",
            "danger",
        )

    return redirect(
        url_for("admin.users")
    )


@admin_bp.route("/users/<int:user_id>/activate", methods=["POST"])
@admin_required
def activate_user(user_id):
    """Activate a user account."""

    user = db.session.get(User, user_id)

    if user is None:
        flash(
            "User not found.",
            "danger",
        )
        return redirect(
            url_for("admin.users")
        )

    if protected_target(user):
        flash(
            "The Super Administrator account cannot be modified.",
            "danger",
        )
        return redirect(
            url_for("admin.users")
        )

    try:
        user.is_active = True

        db.session.commit()

        flash(
            f"User '{user.username}' has been activated.",
            "success",
        )

    except Exception:
        db.session.rollback()

        flash(
            "Unable to activate the user.",
            "danger",
        )

    return redirect(
        url_for("admin.users")
    )


@admin_bp.route("/users/<int:user_id>/deactivate", methods=["POST"])
@admin_required
def deactivate_user(user_id):
    """Deactivate a user account."""

    user = db.session.get(User, user_id)

    if user is None:
        flash(
            "User not found.",
            "danger",
        )
        return redirect(
            url_for("admin.users")
        )

    if protected_target(user):
        flash(
            "The Super Administrator account cannot be modified.",
            "danger",
        )
        return redirect(
            url_for("admin.users")
        )

    try:
        user.is_active = False

        db.session.commit()

        flash(
            f"User '{user.username}' has been deactivated.",
            "success",
        )

    except Exception:
        db.session.rollback()

        flash(
            "Unable to deactivate the user.",
            "danger",
        )

    return redirect(
        url_for("admin.users")
    )


@admin_bp.route("/users/<int:user_id>/role", methods=["POST"])
@admin_required
def change_role(user_id):
    """Change a user's role."""

    user = db.session.get(User, user_id)

    if user is None:
        flash(
            "User not found.",
            "danger",
        )
        return redirect(
            url_for("admin.users")
        )

    if protected_target(user):
        flash(
            "The Super Administrator account cannot be modified.",
            "danger",
        )
        return redirect(
            url_for("admin.users")
        )

    new_role = request.form.get(
        "role",
        ""
    ).strip().lower()

    if new_role not in VALID_ROLES:
        flash(
            "Invalid user role.",
            "danger",
        )
        return redirect(
            url_for("admin.users")
        )

    if (
        new_role == "admin"
        and not is_super_admin(current_user)
    ):
        flash(
            "Only the Super Administrator can grant administrator privileges.",
            "danger",
        )
        return redirect(
            url_for("admin.users")
        )

    try:
        user.role = new_role

        db.session.commit()

        flash(
            f"Role for '{user.username}' changed to '{new_role}'.",
            "success",
        )

    except Exception:
        db.session.rollback()

        flash(
            "Unable to change the user's role.",
            "danger",
        )

    return redirect(
        url_for("admin.users")
    )


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    """Delete a user account."""

    user = db.session.get(User, user_id)

    if user is None:
        flash(
            "User not found.",
            "danger",
        )
        return redirect(
            url_for("admin.users")
        )

    if protected_target(user):
        flash(
            "The Super Administrator account cannot be deleted.",
            "danger",
        )
        return redirect(
            url_for("admin.users")
        )

    if user.id == current_user.id:
        flash(
            "You cannot delete your own account.",
            "danger",
        )
        return redirect(
            url_for("admin.users")
        )

    try:
        username = user.username

        db.session.delete(user)
        db.session.commit()

        flash(
            f"User '{username}' has been deleted.",
            "success",
        )

    except Exception:
        db.session.rollback()

        flash(
            "Unable to delete the user.",
            "danger",
        )

    return redirect(
        url_for("admin.users")
    )