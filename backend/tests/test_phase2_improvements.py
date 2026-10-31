import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.core.security import hash_password, verify_password

client = TestClient(app)


def test_bcrypt_password_hashing_and_verification():
    """Verify passwords are encrypted with bcrypt and properly verified."""
    raw_password = "P@sswordEnterprise2026!"
    hashed = hash_password(raw_password)

    # Must be valid bcrypt hash starting with $2b$
    assert hashed.startswith("$2b$")
    assert hashed != raw_password

    # Correct password succeeds
    assert verify_password(raw_password, hashed) is True

    # Incorrect password fails
    assert verify_password("WrongPassword123", hashed) is False

    # Empty inputs fail safely
    assert verify_password("", hashed) is False
    assert verify_password(raw_password, "") is False


def test_legacy_password_verification_backward_compatibility():
    """Verify legacy salt$sha256 format continues to verify seamlessly."""
    salt = "a1b2c3d4e5f60718"
    import hashlib
    legacy_hash = f"{salt}${hashlib.sha256((salt + 'legacy_secret').encode('utf-8')).hexdigest()}"

    assert verify_password("legacy_secret", legacy_hash) is True
    assert verify_password("wrong_secret", legacy_hash) is False


def test_cors_configuration_strict_origins():
    """Verify CORS middleware restricts Access-Control-Allow-Origin to configured domains."""
    # Request from allowed origin http://localhost:3000
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
    }
    response = client.options("/health", headers=headers)
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"

    # Verify allow-origin is NOT wildcard '*' when credentials are enabled
    assert response.headers.get("access-control-allow-origin") != "*"
