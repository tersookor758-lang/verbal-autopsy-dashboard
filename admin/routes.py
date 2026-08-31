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

from admin import admin_bp
from extensions import db
from models import User


SUPER_ADMIN_USERNAME = "admin"

VALID_ROLES = {
    "user",
    "upload_user",
    "admin",
}


def is_super_admin(user):
    """
    Return True when the account is the permanent
    Super Administrator.
    """

    return (
        user is not None
        and (user.username or "").strip().lower()
        == SUPER_ADMIN_USERNAME
    )


def admin_required():
    """
    Require an authenticated, active administrator.

    Account verification does not control normal access.
    """

    if not current_user.is_authenticated:
        return redirect(
            url_for("auth.login")
        )

    if not current_user.is_active:
        flash(
            "Your account has been deactivated.",
            "danger",
        )
        return redirect(
            url_for("dashboard.index")
        )

    role = (
        current_user.role or ""
    ).strip().lower()

    if role != "admin":
        flash(
            "You do not have permission to access the administrator area.",
            "danger",
        )
        return redirect(
            url_for("dashboard.index")
        )

    return True


def protected_target(user):
    """
    Prevent administrators from modifying the
    permanent Super Administrator account.
    """

    if is_super_admin(user):
        flash(
            "The Super Administrator account cannot be modified.",
            "danger",
        )
        return True

    return False


@admin_bp.after_request
def prevent_admin_cache(response):
    response.headers["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, max-age=0"
    )
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


@admin_bp.route("/")
@login_required
def index():
    access = admin_required()

    if access is not True:
        return access

    stats = {
        "total_users": User.query.count(),
        "verified_users": User.query.filter_by(
            is_verified=True
        ).count(),
        "pending_users": User.query.filter_by(
            is_verified=False
        ).count(),
        "active_users": User.query.filter_by(
            is_active=True
        ).count(),
        "inactive_users": User.query.filter_by(
            is_active=False
        ).count(),
        "admin_users": User.query.filter(
            User.role.in_(
                ["admin", "administrator"]
            )
        ).count(),
        "regular_users": User.query.filter_by(
            role="user"
        ).count(),
        "upload_users": User.query.filter_by(
            role="upload_user"
        ).count(),
    }

    recent_users = (
        User.query
        .order_by(User.created_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "admin/index.html",
        **stats,
        recent_users=recent_users,
    )


@admin_bp.route("/users")
@login_required
def users():
    access = admin_required()

    if access is not True:
        return access

    users = (
        User.query
        .order_by(User.created_at.desc())
        .all()
    )

    return render_template(
        "admin/users.html",
        users=users,
    )


@admin_bp.route(
    "/users/<int:user_id>/verify",
    methods=["POST"],
)
@login_required
def verify_user(user_id):
    access = admin_required()

    if access is not True:
        return access

    user = User.query.get_or_404(user_id)

    if protected_target(user):
        return redirect(
            url_for("admin.users")
        )

    try:
        user.is_verified = True

        db.session.commit()

    except Exception:
        db.session.rollback()

        flash(
            "The verification status could not be changed. Please try again.",
            "danger",
        )

        return redirect(
            url_for("admin.users")
        )

    flash(
        f"User '{user.username}' has been marked as verified.",
        "success",
    )

    return redirect(
        url_for("admin.users")
    )


@admin_bp.route(
    "/users/<int:user_id>/unverify",
    methods=["POST"],
)
@login_required
def unverify_user(user_id):
    access = admin_required()

    if access is not True:
        return access

    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash(
            "You cannot change your own verification status.",
            "danger",
        )

        return redirect(
            url_for("admin.users")
        )

    if protected_target(user):
        return redirect(
            url_for("admin.users")
        )

    try:
        user.is_verified = False

        db.session.commit()

    except Exception:
        db.session.rollback()

        flash(
            "The verification status could not be changed. Please try again.",
            "danger",
        )

        return redirect(
            url_for("admin.users")
        )

    flash(
        f"User '{user.username}' is now marked as unverified.",
        "warning",
    )

    return redirect(
        url_for("admin.users")
    )


@admin_bp.route(
    "/users/<int:user_id>/activate",
    methods=["POST"],
)
@login_required
def activate_user(user_id):
    access = admin_required()

    if access is not True:
        return access

    user = User.query.get_or_404(user_id)

    if protected_target(user):
        return redirect(
            url_for("admin.users")
        )

    try:
        user.is_active = True

        db.session.commit()

    except Exception:
        db.session.rollback()

        flash(
            "The account could not be activated. Please try again.",
            "danger",
        )

        return redirect(
            url_for("admin.users")
        )

    flash(
        f"User '{user.username}' has been activated.",
        "success",
    )

    return redirect(
        url_for("admin.users")
    )


@admin_bp.route(
    "/users/<int:user_id>/deactivate",
    methods=["POST"],
)
@login_required
def deactivate_user(user_id):
    access = admin_required()

    if access is not True:
        return access

    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash(
            "You cannot deactivate your own account.",
            "danger",
        )

        return redirect(
            url_for("admin.users")
        )

    if protected_target(user):
        return redirect(
            url_for("admin.users")
        )

    try:
        user.is_active = False

        db.session.commit()

    except Exception:
        db.session.rollback()

        flash(
            "The account could not be deactivated. Please try again.",
            "danger",
        )

        return redirect(
            url_for("admin.users")
        )

    flash(
        f"User '{user.username}' has been deactivated.",
        "warning",
    )

    return redirect(
        url_for("admin.users")
    )


@admin_bp.route(
    "/users/<int:user_id>/role",
    methods=["POST"],
)
@login_required
def change_role(user_id):
    access = admin_required()

    if access is not True:
        return access

    user = User.query.get_or_404(user_id)

    new_role = (
        request.form.get(
            "role",
            "",
        )
        .strip()
        .lower()
    )

    if user.id == current_user.id:
        flash(
            "You cannot change your own administrator role.",
            "danger",
        )

        return redirect(
            url_for("admin.users")
        )

    if protected_target(user):
        return redirect(
            url_for("admin.users")
        )

    if new_role not in VALID_ROLES:
        flash(
            "Invalid user role.",
            "danger",
        )

        return redirect(
            url_for("admin.users")
        )

    try:
        user.role = new_role

        db.session.commit()

    except Exception:
        db.session.rollback()

        flash(
            "The user role could not be changed. Please try again.",
            "danger",
        )

        return redirect(
            url_for("admin.users")
        )

    flash(
        f"Role for '{user.username}' changed to '{new_role}'.",
        "success",
    )

    return redirect(
        url_for("admin.users")
    )


@admin_bp.route(
    "/users/<int:user_id>/delete",
    methods=["POST"],
)
@login_required
def delete_user(user_id):
    access = admin_required()

    if access is not True:
        return access

    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash(
            "You cannot delete your own account.",
            "danger",
        )

        return redirect(
            url_for("admin.users")
        )

    if protected_target(user):
        return redirect(
            url_for("admin.users")
        )

    username = user.username

    try:
        db.session.delete(user)
        db.session.commit()

    except Exception:
        db.session.rollback()

        flash(
            "The user could not be deleted. Please try again.",
            "danger",
        )

        return redirect(
            url_for("admin.users")
        )

    flash(
        f"User '{username}' has been deleted.",
        "success",
    )

    return redirect(
        url_for("admin.users")
    )