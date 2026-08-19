"""
Administrator Routes

Handles:
- Admin dashboard
- User management
- User verification / approval
- Account activation/deactivation
- Role management
- User deletion
"""

from flask import (
    flash,
    make_response,
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
    Allow access only to administrator accounts.
    """

    if not current_user.is_authenticated:
        return redirect(
            url_for("auth.login")
        )

    role = (
        current_user.role or ""
    ).strip().lower()

    if role != "admin":
        flash(
            "You do not have permission to access "
            "the administrator area.",
            "danger",
        )

        return redirect(
            url_for("dashboard.index")
        )

    return True


# ==========================================================
# Prevent Browser Caching of Admin Pages
# ==========================================================

@admin_bp.after_request
def prevent_admin_cache(response):
    """
    Prevent the browser from displaying stale administrator
    pages after user verification, activation or role changes.
    """

    response.headers["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, max-age=0"
    )

    response.headers["Pragma"] = "no-cache"

    response.headers["Expires"] = "0"

    return response


# ==========================================================
# Admin Dashboard
# ==========================================================

@admin_bp.route("/")
@login_required
def index():
    """
    Display administrator statistics
    and recent users.
    """

    access = admin_required()

    if access is not True:
        return access

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

    admin_users = User.query.filter(
        User.role.in_(["admin", "administrator"])
    ).count()

    regular_users = User.query.filter_by(
        role="user"
    ).count()

    upload_users = User.query.filter_by(
        role="upload_user"
    ).count()

    recent_users = (
        User.query
        .order_by(
            User.created_at.desc()
        )
        .limit(5)
        .all()
    )

    response = make_response(
        render_template(
            "admin/index.html",
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
    )

    return response


# ==========================================================
# User Management
# ==========================================================

@admin_bp.route("/users")
@login_required
def users():
    """
    Display all registered users.

    Verification and activation are deliberately displayed
    as separate account states.
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

    response = make_response(
        render_template(
            "admin/users.html",
            users=users,
        )
    )

    return response


# ==========================================================
# Verify / Approve User
# ==========================================================

@admin_bp.route(
    "/users/<int:user_id>/verify",
    methods=["POST"],
)
@login_required
def verify_user(user_id):
    """
    Approve a user account.

    Verification means the administrator has approved
    the account.

    Activation is handled separately.
    """

    access = admin_required()

    if access is not True:
        return access

    user = User.query.get_or_404(
        user_id
    )

    user.is_verified = True

    # A verified account should also be usable.
    # This avoids the confusing state where an administrator
    # approves an account but leaves it inaccessible.
    user.is_active = True

    db.session.commit()

    flash(
        f"User '{user.username}' has been verified "
        "and activated.",
        "success",
    )

    return redirect(
        url_for("admin.users")
    )


# ==========================================================
# Unverify User
# ==========================================================

@admin_bp.route(
    "/users/<int:user_id>/unverify",
    methods=["POST"],
)
@login_required
def unverify_user(user_id):
    """
    Remove verification from a user account.

    The account is also deactivated because an unverified
    account should not retain normal access.
    """

    access = admin_required()

    if access is not True:
        return access

    user = User.query.get_or_404(
        user_id
    )

    if user.id == current_user.id:
        flash(
            "You cannot remove verification from your "
            "own administrator account.",
            "danger",
        )

        return redirect(
            url_for("admin.users")
        )

    user.is_verified = False
    user.is_active = False

    db.session.commit()

    flash(
        f"User '{user.username}' is now pending verification.",
        "warning",
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
    """
    Activate a previously deactivated account.

    Activation does not automatically verify an account.
    """

    access = admin_required()

    if access is not True:
        return access

    user = User.query.get_or_404(
        user_id
    )

    user.is_active = True

    db.session.commit()

    flash(
        f"User '{user.username}' has been activated.",
        "success",
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
    """
    Deactivate a user without deleting the account.
    """

    access = admin_required()

    if access is not True:
        return access

    user = User.query.get_or_404(
        user_id
    )

    if user.id == current_user.id:
        flash(
            "You cannot deactivate your own account.",
            "danger",
        )

        return redirect(
            url_for("admin.users")
        )

    user.is_active = False

    db.session.commit()

    flash(
        f"User '{user.username}' has been deactivated.",
        "warning",
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
    """
    Change a user's role.
    """

    access = admin_required()

    if access is not True:
        return access

    user = User.query.get_or_404(
        user_id
    )

    if user.id == current_user.id:
        flash(
            "You cannot change your own administrator role.",
            "danger",
        )

        return redirect(
            url_for("admin.users")
        )

    new_role = request.form.get(
        "role",
        "",
    ).strip().lower()

    allowed_roles = {
        "user",
        "upload_user",
        "admin",
    }

    if new_role not in allowed_roles:
        flash(
            "Invalid user role.",
            "danger",
        )

        return redirect(
            url_for("admin.users")
        )

    user.role = new_role

    db.session.commit()

    flash(
        f"Role for '{user.username}' changed to "
        f"'{new_role}'.",
        "success",
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
    """
    Permanently delete a user account.
    """

    access = admin_required()

    if access is not True:
        return access

    user = User.query.get_or_404(
        user_id
    )

    if user.id == current_user.id:
        flash(
            "You cannot delete your own account.",
            "danger",
        )

        return redirect(
            url_for("admin.users")
        )

    db.session.delete(user)

    db.session.commit()

    flash(
        f"User '{user.username}' has been deleted.",
        "success",
    )

    return redirect(
        url_for("admin.users")
    )