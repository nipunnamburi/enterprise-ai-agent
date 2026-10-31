from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Any
import hashlib
import secrets
import bcrypt
from jose import jwt
from app.core.config import settings


def hash_password(password: str) -> str:
    """Hash password using industry-standard bcrypt with auto-generated salt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed_bytes = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash, with backward-compatibility for legacy sha256 hashes."""
    if not hashed_password or not plain_password:
        return False

    # Standard Bcrypt format: $2a$, $2b$, or $2y$
    if hashed_password.startswith(("$2a$", "$2b$", "$2y$")):
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8")
            )
        except Exception:
            return False

    # Legacy fallback: salt$sha256hash
    if "$" in hashed_password:
        try:
            salt, original_hash = hashed_password.split("$", 1)
            test_hash = hashlib.sha256((salt + plain_password).encode("utf-8")).hexdigest()
            return secrets.compare_digest(original_hash, test_hash)
        except Exception:
            return False

    return False


def get_password_hash(password: str) -> str:
    """Convenience alias for hash_password."""
    return hash_password(password)


def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generate signed JWT access token with expiration timestamp."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
