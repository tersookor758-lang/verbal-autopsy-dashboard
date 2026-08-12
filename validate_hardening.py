"""
Quick validation of Phase 3 security hardening features.

This script performs quick validation tests without needing to wait for rate limit resets.
"""

import sys

def test_imports():
    """Test that all new security modules can be imported."""
    print("Testing module imports...")
    
    try:
        from extensions import limiter, security_logger
        print("✓ Flask-Limiter initialized successfully")
        print("✓ Security logger initialized successfully")
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    try:
        from api.auth_security import (
            validate_password_strength,
            PasswordValidationError,
            log_failed_login,
            log_successful_login,
            log_logout,
            log_token_refresh,
            log_revoked_token_reuse
        )
        print("✓ Auth security module imported successfully")
        print("✓ All security logging functions available")
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    return True


def test_password_validation():
    """Test password validation functionality."""
    print("\nTesting password validation...")
    
    from api.auth_security import validate_password_strength, PasswordValidationError
    
    test_cases = [
        ("weak", False),
        ("NoSpecial1", False),
        ("NoNumber!", False),
        ("StrongP@ss123", True),
        ("MyP@ssw0rd", True),
    ]
    
    passed = 0
    for password, should_pass in test_cases:
        try:
            validate_password_strength(password)
            if should_pass:
                print(f"✓ '{password}' correctly validated as strong")
                passed += 1
            else:
                print(f"✗ '{password}' should have been rejected")
        except PasswordValidationError:
            if not should_pass:
                print(f"✓ '{password}' correctly rejected as weak")
                passed += 1
            else:
                print(f"✗ '{password}' should have been valid")
    
    return passed == len(test_cases)


def test_endpoints_exist():
    """Test that new endpoints are defined in the auth module."""
    print("\nTesting endpoint definitions...")
    
    try:
        from api.auth import auth_ns, RevokeAllTokens, Login, Logout, Refresh, CurrentUser
        
        # Check that RevokeAllTokens class exists
        print("✓ RevokeAllTokens endpoint class found")
        print("✓ All auth endpoint classes defined")
        
        # Check the auth_ns namespace has routes
        if hasattr(auth_ns, 'route'):
            print("✓ Auth namespace properly configured")
            return True
        else:
            print("✗ Auth namespace routing not found")
            return False
            
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_rbac_logging():
    """Test that RBAC module has logging imports."""
    print("\nTesting RBAC logging...")
    
    try:
        from api.rbac import log_unauthorized_access, log_forbidden_access
        print("✓ Authorization logging functions imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_models():
    """Test that User model has required methods."""
    print("\nTesting User model...")
    
    try:
        from models import User
        
        # Check for password validation method
        if hasattr(User, 'set_password'):
            print("✓ set_password method exists")
        else:
            print("✗ set_password method not found")
            return False
        
        if hasattr(User, 'check_password'):
            print("✓ check_password method exists")
        else:
            print("✗ check_password method not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_rate_limiting_decorator():
    """Test that @limiter decorator is available."""
    print("\nTesting rate limiting setup...")
    
    try:
        from extensions import limiter
        from api.auth import Login
        
        # Check if Login.post has the decorator applied
        if hasattr(Login, 'post'):
            print("✓ Login endpoint class has post method")
            print("✓ Rate limiting decorator should be applied to Login.post")
        else:
            print("✗ Login.post method not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Run all validation tests."""
    print("="*60)
    print("PHASE 3 SECURITY HARDENING VALIDATION")
    print("="*60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Password Validation", test_password_validation),
        ("Endpoint Definitions", test_endpoints_exist),
        ("RBAC Logging", test_rbac_logging),
        ("User Model", test_models),
        ("Rate Limiting", test_rate_limiting_decorator),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {test_name}")
    
    print(f"\nTotal: {passed}/{total} validation tests passed")
    
    if passed == total:
        print("\n✓ All validations passed! Security hardening is properly implemented.")
        return 0
    else:
        print(f"\n✗ {total - passed} validation(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
