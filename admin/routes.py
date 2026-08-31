from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from admin import admin_bp
from extensions import db
from models import User


def admin_required():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))

    if (current_user.role or "").strip().lower() != "admin":
        flash("You do not have permission to access the administrator area.", "danger")
        return redirect(url_for("dashboard.index"))

    return True


@admin_bp.after_request
def prevent_admin_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
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
        "verified_users": User.query.filter_by(is_verified=True).count(),
        "pending_users": User.query.filter_by(is_verified=False).count(),
        "active_users": User.query.filter_by(is_active=True).count(),
        "inactive_users": User.query.filter_by(is_active=False).count(),
        "admin_users": User.query.filter(User.role.in_(["admin", "administrator"])).count(),
        "regular_users": User.query.filter_by(role="user").count(),
        "upload_users": User.query.filter_by(role="upload_user").count(),
    }

    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

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

    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users)


@admin_bp.route("/users/<int:user_id>/verify", methods=["POST"])
@login_required
def verify_user(user_id):
    access = admin_required()
    if access is not True:
        return access

    user = User.query.get_or_404(user_id)
    user.is_verified = True
    user.is_active = True
    db.session.commit()

    flash(f"User '{user.username}' has been approved and activated.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/unverify", methods=["POST"])
@login_required
def unverify_user(user_id):
    access = admin_required()
    if access is not True:
        return access

    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash("You cannot remove verification from your own account.", "danger")
        return redirect(url_for("admin.users"))

    user.is_verified = False
    user.is_active = False
    db.session.commit()

    flash(f"User '{user.username}' is now pending verification.", "warning")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/activate", methods=["POST"])
@login_required
def activate_user(user_id):
    access = admin_required()
    if access is not True:
        return access

    user = User.query.get_or_404(user_id)

    if not user.is_verified:
        flash("The user must be verified before the account can be activated.", "warning")
        return redirect(url_for("admin.users"))

    user.is_active = True
    db.session.commit()

    flash(f"User '{user.username}' has been activated.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/deactivate", methods=["POST"])
@login_required
def deactivate_user(user_id):
    access = admin_required()
    if access is not True:
        return access

    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash("You cannot deactivate your own account.", "danger")
        return redirect(url_for("admin.users"))

    user.is_active = False
    db.session.commit()

    flash(f"User '{user.username}' has been deactivated.", "warning")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/role", methods=["POST"])
@login_required
def change_role(user_id):
    access = admin_required()
    if access is not True:
        return access

    user = User.query.get_or_404(user_id)
    new_role = request.form.get("role", "").strip().lower()
    allowed_roles = {"user", "upload_user", "admin"}

    if user.id == current_user.id:
        flash("You cannot change your own administrator role.", "danger")
        return redirect(url_for("admin.users"))

    if new_role not in allowed_roles:
        flash("Invalid user role.", "danger")
        return redirect(url_for("admin.users"))

    if user.role in {"admin", "administrator"} and new_role != "admin":
        admin_count = User.query.filter(
            User.role.in_(["admin", "administrator"])
        ).count()

        if admin_count <= 1:
            flash("You cannot remove the last administrator.", "danger")
            return redirect(url_for("admin.users"))

    user.role = new_role
    db.session.commit()

    flash(f"Role for '{user.username}' changed to '{new_role}'.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):
    access = admin_required()
    if access is not True:
        return access

    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash("You cannot delete your own account.", "danger")
        return redirect(url_for("admin.users"))

    if user.role in {"admin", "administrator"}:
        admin_count = User.query.filter(
            User.role.in_(["admin", "administrator"])
        ).count()

        if admin_count <= 1:
            flash("You cannot delete the last administrator.", "danger")
            return redirect(url_for("admin.users"))

    db.session.delete(user)
    db.session.commit()

    flash(f"User '{user.username}' has been deleted.", "success")
    return redirect(url_for("admin.users"))