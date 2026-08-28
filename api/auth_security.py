"""
Authentication security utilities.

Provides password validation, security logging,
and authentication-related security checks.
"""

import re

from extensions import security_logger


# ==========================================================
# Password Validation
# ==========================================================

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
        r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]",
        password,
    ):
        raise PasswordValidationError(
            "Password must contain at least one special character "
            "(!@#$%^&*)."
        )

    return True


# ==========================================================
# Security Logging
# ==========================================================

def log_failed_login(
    username,
    ip_address,
    reason="Invalid credentials",
):
    """Log a failed login attempt."""

    security_logger.warning(
        f"FAILED_LOGIN | username={username} | "
        f"ip={ip_address} | reason={reason}"
    )


def log_successful_login(
    username,
    ip_address,
    user_id,
):
    """Log a successful login."""

    security_logger.info(
        f"SUCCESSFUL_LOGIN | username={username} | "
        f"user_id={user_id} | ip={ip_address}"
    )


def log_logout(
    username,
    user_id,
    ip_address,
):
    """Log a logout event."""

    security_logger.info(
        f"LOGOUT | username={username} | "
        f"user_id={user_id} | ip={ip_address}"
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
            f"TOKEN_REFRESH | username={username} | "
            f"user_id={user_id} | status=SUCCESS"
        )
    else:
        security_logger.warning(
            f"TOKEN_REFRESH | username={username} | "
            f"user_id={user_id} | status=FAILED | "
            f"reason={reason}"
        )


def log_unauthorized_access(
    endpoint,
    user_info,
    ip_address,
):
    """Log an unauthorized access attempt."""

    security_logger.warning(
        f"UNAUTHORIZED_ACCESS | endpoint={endpoint} | "
        f"user={user_info} | ip={ip_address}"
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
        f"FORBIDDEN_ACCESS | endpoint={endpoint} | "
        f"username={username} | user_id={user_id} | "
        f"required_role={required_role} | "
        f"actual_role={actual_role} | ip={ip_address}"
    )


def log_revoked_token_reuse(
    username,
    user_id,
    ip_address,
    token_type="refresh",
):
    """Log an attempt to reuse a revoked token."""

    security_logger.warning(
        f"REVOKED_TOKEN_REUSE | token_type={token_type} | "
        f"username={username} | user_id={user_id} | "
        f"ip={ip_address}"
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
        f"RATE_LIMIT_EXCEEDED | endpoint={endpoint} | "
        f"user={user_info} | ip={ip_address}"
    )


def log_password_validation_failure(
    username,
    reason,
):
    """Log a password validation failure."""

    security_logger.warning(
        f"PASSWORD_VALIDATION_FAILED | "
        f"username={username} | reason={reason}"
    )