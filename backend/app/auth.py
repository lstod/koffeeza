from __future__ import annotations

import hashlib
import hmac
import os
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User

_bearer = HTTPBearer()

SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    _key_file = os.path.join(os.path.dirname(__file__), "..", ".secret_key")
    _key_file = os.path.abspath(_key_file)
    try:
        with open(_key_file) as f:
            SECRET_KEY = f.read().strip()
    except FileNotFoundError:
        SECRET_KEY = os.urandom(32).hex()
        with open(_key_file, "w") as f:
            f.write(SECRET_KEY)

ALGORITHM = "HS256"
TOKEN_EXPIRE_DAYS = 365


def hash_pin(pin: str) -> str:
    """Hash a PIN using SHA-256 with a salt. Sufficient for short numeric PINs."""
    salt = os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, iterations=100_000)
    return salt.hex() + ":" + h.hex()


def verify_pin(pin: str, pin_hash: str) -> bool:
    salt_hex, hash_hex = pin_hash.split(":")
    salt = bytes.fromhex(salt_hex)
    h = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, iterations=100_000)
    return hmac.compare_digest(h.hex(), hash_hex)


def create_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(UTC) + timedelta(days=TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token") from exc

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    return user
