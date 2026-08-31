"""
Authentication security utilities.

Provides password validation, security logging,
and authentication-related security checks.
"""

import re

from extensions import security_logger


class PasswordValidationError(Exception):
    """Raised when a password does not meet security requirements."""

    pass


def validate_password_strength(password):
    """
    Validate that a password meets security requirements.

    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """

    if not password:
        raise PasswordValidationError(
            "Password is required."
        )

    if len(password) < 8:
        raise PasswordValidationError(
            "Password must be at least 8 characters long."
        )

    if not re.search(r"[A-Z]", password):
        raise PasswordValidationError(
            "Password must contain at least one uppercase letter."
        )

    if not re.search(r"[a-z]", password):
        raise PasswordValidationError(
            "Password must contain at least one lowercase letter."
        )

    if not re.search(r"[0-9]", password):
        raise PasswordValidationError(
            "Password must contain at least one digit."
        )

    if not re.search(
        r"""[!@#$%^&*()_+\-=\[\]{}|;:,.<>?/]""",
        password,
    ):
        raise PasswordValidationError(
            "Password must contain at least one special character."
        )

    return True


def _safe_log_value(value):
    """Remove control characters before writing values to security logs."""

    if value is None:
        return "unknown"

    return re.sub(
        r"[\r\n\t\x00-\x1f\x7f]",
        " ",
        str(value),
    ).strip()


def log_failed_login(
    username,
    ip_address,
    reason="Invalid credentials",
):
    """Log a failed login attempt."""

    security_logger.warning(
        "FAILED_LOGIN | username=%s | ip=%s | reason=%s",
        _safe_log_value(username),
        _safe_log_value(ip_address),
        _safe_log_value(reason),
    )


def log_successful_login(
    username,
    ip_address,
    user_id,
):
    """Log a successful login."""

    security_logger.info(
        "SUCCESSFUL_LOGIN | username=%s | user_id=%s | ip=%s",
        _safe_log_value(username),
        _safe_log_value(user_id),
        _safe_log_value(ip_address),
    )


def log_logout(
    username,
    user_id,
    ip_address,
):
    """Log a logout event."""

    security_logger.info(
        "LOGOUT | username=%s | user_id=%s | ip=%s",
        _safe_log_value(username),
        _safe_log_value(user_id),
        _safe_log_value(ip_address),
    )


def log_token_refresh(
    username,
    user_id,
    success=True,
    reason=None,
):
    """Log a token refresh attempt."""

    if success:
        security_logger.info(
            "TOKEN_REFRESH | username=%s | user_id=%s | status=SUCCESS",
            _safe_log_value(username),
            _safe_log_value(user_id),
        )
        return

    security_logger.warning(
        "TOKEN_REFRESH | username=%s | user_id=%s | "
        "status=FAILED | reason=%s",
        _safe_log_value(username),
        _safe_log_value(user_id),
        _safe_log_value(reason),
    )


def log_unauthorized_access(
    endpoint,
    user_info,
    ip_address,
):
    """Log an unauthorized access attempt."""

    security_logger.warning(
        "UNAUTHORIZED_ACCESS | endpoint=%s | user=%s | ip=%s",
        _safe_log_value(endpoint),
        _safe_log_value(user_info),
        _safe_log_value(ip_address),
    )


def log_forbidden_access(
    endpoint,
    username,
    user_id,
    required_role,
    actual_role,
    ip_address,
):
    """Log a forbidden access attempt."""

    security_logger.warning(
        "FORBIDDEN_ACCESS | endpoint=%s | username=%s | "
        "user_id=%s | required_role=%s | actual_role=%s | ip=%s",
        _safe_log_value(endpoint),
        _safe_log_value(username),
        _safe_log_value(user_id),
        _safe_log_value(required_role),
        _safe_log_value(actual_role),
        _safe_log_value(ip_address),
    )


def log_revoked_token_reuse(
    username,
    user_id,
    ip_address,
    token_type="refresh",
):
    """Log an attempt to reuse a revoked token."""

    security_logger.warning(
        "REVOKED_TOKEN_REUSE | token_type=%s | username=%s | "
        "user_id=%s | ip=%s",
        _safe_log_value(token_type),
        _safe_log_value(username),
        _safe_log_value(user_id),
        _safe_log_value(ip_address),
    )


def log_rate_limit_exceeded(
    endpoint,
    ip_address,
    username=None,
):
    """Log when a rate limit is exceeded."""

    user_info = (
        username
        if username
        else "anonymous"
    )

    security_logger.warning(
        "RATE_LIMIT_EXCEEDED | endpoint=%s | user=%s | ip=%s",
        _safe_log_value(endpoint),
        _safe_log_value(user_info),
        _safe_log_value(ip_address),
    )


def log_password_validation_failure(
    username,
    reason,
):
    """Log a password validation failure."""

    security_logger.warning(
        "PASSWORD_VALIDATION_FAILED | username=%s | reason=%s",
        _safe_log_value(username),
        _safe_log_value(reason),
    )