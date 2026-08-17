"""
Administrator Routes

Handles:
- Admin dashboard
- User management
- Approving new accounts
- Activating accounts
- Deactivating accounts
- Changing user roles
- Deleting user accounts
"""

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


# ==========================================================
# Admin Access Protection
# ==========================================================

def admin_required():
    """
    Ensure that the current user is an administrator.

    Returns:
        True when access is allowed.
        Redirect response when access is denied.
    """

    if not current_user.is_authenticated:

        return redirect(
            url_for("auth.login")
        )

    role = (
        current_user.role or ""
    ).strip().lower()

    if role not in {
        "admin",
        "administrator",
    }:

        flash(
            "You do not have permission to access "
            "the administrator area.",
            "danger"
        )

        return redirect(
            url_for("dashboard.index")
        )

    return True


# ==========================================================
# Admin Dashboard
# ==========================================================

@admin_bp.route("/")
@login_required
def index():
    """
    Display the administrator dashboard.
    """

    access = admin_required()

    if access is not True:
        return access

    # ------------------------------------------------------
    # User Statistics
    # ------------------------------------------------------

    total_users = User.query.count()

    pending_users = User.query.filter(
        User.is_verified.is_(False)
    ).count()

    active_users = User.query.filter(
        User.is_active.is_(True)
    ).count()

    inactive_users = User.query.filter(
        User.is_active.is_(False)
    ).count()

    admin_users = User.query.filter(
        User.role.in_([
            "admin",
            "administrator",
        ])
    ).count()

    regular_users = User.query.filter(
        User.role == "user"
    ).count()

    upload_users = User.query.filter(
        User.role == "upload_user"
    ).count()

    # ------------------------------------------------------
    # Recent Users
    # ------------------------------------------------------

    recent_users = (
        User.query
        .order_by(
            User.created_at.desc()
        )
        .limit(5)
        .all()
    )

    return render_template(
        "admin/index.html",
        total_users=total_users,
        pending_users=pending_users,
        active_users=active_users,
        inactive_users=inactive_users,
        admin_users=admin_users,
        regular_users=regular_users,
        upload_users=upload_users,
        recent_users=recent_users,
    )


# ==========================================================
# User Management
# ==========================================================

@admin_bp.route("/users")
@login_required
def users():
    """
    Display all registered users.
    """

    access = admin_required()

    if access is not True:
        return access

    users = (
        User.query
        .order_by(
            User.created_at.desc()
        )
        .all()
    )

    pending_users = [
        user
        for user in users
        if not user.is_verified
        and user.role not in {
            "admin",
            "administrator",
        }
    ]

    return render_template(
        "admin/users.html",
        users=users,
        pending_users=pending_users,
    )


# ==========================================================
# Approve User
# ==========================================================

@admin_bp.route(
    "/users/<int:user_id>/approve",
    methods=["POST"],
)
@login_required
def approve_user(user_id):

    access = admin_required()

    if access is not True:
        return access

    user = User.query.get_or_404(user_id)

    if user.role in {
        "admin",
        "administrator",
    }:

        flash(
            "Administrator accounts do not require approval.",
            "info"
        )

        return redirect(
            url_for("admin.users")
        )

    user.is_verified = True
    user.is_active = True

    db.session.commit()

    flash(
        f"User '{user.username}' has been approved.",
        "success"
    )

    return redirect(
        url_for("admin.users")
    )


# ==========================================================
# Activate User
# ==========================================================

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

    user.is_active = True

    db.session.commit()

    flash(
        f"User '{user.username}' has been activated.",
        "success"
    )

    return redirect(
        url_for("admin.users")
    )


# ==========================================================
# Deactivate User
# ==========================================================

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
            "danger"
        )

        return redirect(
            url_for("admin.users")
        )

    user.is_active = False

    db.session.commit()

    flash(
        f"User '{user.username}' has been deactivated.",
        "warning"
    )

    return redirect(
        url_for("admin.users")
    )


# ==========================================================
# Change User Role
# ==========================================================

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

    new_role = request.form.get(
        "role",
        ""
    ).strip().lower()

    allowed_roles = {
        "user",
        "upload_user",
        "admin",
    }

    if new_role not in allowed_roles:

        flash(
            "Invalid user role.",
            "danger"
        )

        return redirect(
            url_for("admin.users")
        )

    if user.id == current_user.id:

        flash(
            "You cannot change your own administrator role.",
            "danger"
        )

        return redirect(
            url_for("admin.users")
        )

    user.role = new_role

    if new_role == "admin":

        user.is_verified = True

    db.session.commit()

    flash(
        f"Role for '{user.username}' changed to "
        f"'{new_role}'.",
        "success"
    )

    return redirect(
        url_for("admin.users")
    )


# ==========================================================
# Delete User
# ==========================================================

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
            "danger"
        )

        return redirect(
            url_for("admin.users")
        )

    db.session.delete(user)

    db.session.commit()

    flash(
        f"User '{user.username}' has been deleted.",
        "success"
    )

    return redirect(
        url_for("admin.users")
    )