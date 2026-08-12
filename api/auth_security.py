"""
Authentication security utilities.

Provides functions for password validation, security logging, and other auth-related security checks.
"""

import re
from datetime import datetime, timedelta
from extensions import security_logger


# ==========================================================
# Password Validation
# ==========================================================

class PasswordValidationError(Exception):
    """Raised when password doesn't meet security requirements."""
    pass


def validate_password_strength(password):
    """
    Validate password meets security requirements.
    
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character (!@#$%^&*)
    
    Args:
        password (str): The password to validate
        
    Raises:
        PasswordValidationError: If password doesn't meet requirements
        
    Returns:
        bool: True if password is valid
    """
    
    if not password:
        raise PasswordValidationError("Password is required.")
    
    if len(password) < 8:
        raise PasswordValidationError(
            "Password must be at least 8 characters long."
        )
    
    if not re.search(r'[A-Z]', password):
        raise PasswordValidationError(
            "Password must contain at least one uppercase letter."
        )
    
    if not re.search(r'[a-z]', password):
        raise PasswordValidationError(
            "Password must contain at least one lowercase letter."
        )
    
    if not re.search(r'[0-9]', password):
        raise PasswordValidationError(
            "Password must contain at least one digit."
        )
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
        raise PasswordValidationError(
            "Password must contain at least one special character (!@#$%^&*)."
        )
    
    return True


# ==========================================================
# Security Logging (Never log sensitive data!)
# ==========================================================

def log_failed_login(username, ip_address, reason="Invalid credentials"):
    """
    Log a failed login attempt.
    
    IMPORTANT: Never log the password or any raw sensitive data.
    
    Args:
        username (str): Username that attempted login
        ip_address (str): IP address of login attempt
        reason (str): Reason for failure
    """
    security_logger.warning(
        f"FAILED_LOGIN | username={username} | ip={ip_address} | reason={reason}"
    )


def log_successful_login(username, ip_address, user_id):
    """
    Log a successful login.
    
    Args:
        username (str): Username that logged in
        ip_address (str): IP address of login
        user_id (int): User ID
    """
    security_logger.info(
        f"SUCCESSFUL_LOGIN | username={username} | user_id={user_id} | ip={ip_address}"
    )


def log_logout(username, user_id, ip_address):
    """
    Log a logout event.
    
    Args:
        username (str): Username that logged out
        user_id (int): User ID
        ip_address (str): IP address
    """
    security_logger.info(
        f"LOGOUT | username={username} | user_id={user_id} | ip={ip_address}"
    )


def log_token_refresh(username, user_id, success=True, reason=None):
    """
    Log a token refresh attempt.
    
    Args:
        username (str): Username attempting refresh
        user_id (int): User ID
        success (bool): Whether refresh was successful
        reason (str): Reason for failure (if not successful)
    """
    if success:
        security_logger.info(
            f"TOKEN_REFRESH | username={username} | user_id={user_id} | status=SUCCESS"
        )
    else:
        security_logger.warning(
            f"TOKEN_REFRESH | username={username} | user_id={user_id} | "
            f"status=FAILED | reason={reason}"
        )


def log_unauthorized_access(endpoint, user_info, ip_address):
    """
    Log an unauthorized access attempt (no token).
    
    Args:
        endpoint (str): API endpoint attempted
        user_info (str): User identifier or "anonymous"
        ip_address (str): IP address
    """
    security_logger.warning(
        f"UNAUTHORIZED_ACCESS | endpoint={endpoint} | user={user_info} | ip={ip_address}"
    )


def log_forbidden_access(endpoint, username, user_id, required_role, actual_role, ip_address):
    """
    Log a forbidden access attempt (insufficient permissions).
    
    Args:
        endpoint (str): API endpoint attempted
        username (str): Username
        user_id (int): User ID
        required_role (str): Role required
        actual_role (str): User's actual role
        ip_address (str): IP address
    """
    security_logger.warning(
        f"FORBIDDEN_ACCESS | endpoint={endpoint} | username={username} | "
        f"user_id={user_id} | required_role={required_role} | "
        f"actual_role={actual_role} | ip={ip_address}"
    )


def log_revoked_token_reuse(username, user_id, ip_address, token_type="refresh"):
    """
    Log an attempt to reuse a revoked token.
    
    Args:
        username (str): Username
        user_id (int): User ID
        ip_address (str): IP address
        token_type (str): Type of token (refresh, access)
    """
    security_logger.warning(
        f"REVOKED_TOKEN_REUSE | token_type={token_type} | username={username} | "
        f"user_id={user_id} | ip={ip_address}"
    )


def log_rate_limit_exceeded(endpoint, ip_address, username=None):
    """
    Log when rate limit is exceeded.
    
    Args:
        endpoint (str): API endpoint
        ip_address (str): IP address
        username (str): Username if available
    """
    user_info = username if username else "anonymous"
    security_logger.warning(
        f"RATE_LIMIT_EXCEEDED | endpoint={endpoint} | user={user_info} | ip={ip_address}"
    )


def log_password_validation_failure(username, reason):
    """
    Log when password validation fails.
    
    Args:
        username (str): Username
        reason (str): Reason for validation failure
    """
    security_logger.warning(
        f"PASSWORD_VALIDATION_FAILED | username={username} | reason={reason}"
    )
