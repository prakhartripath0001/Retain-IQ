
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
if len(SECRET_KEY) < 32:
    raise RuntimeError(
        "Set JWT_SECRET_KEY to a securely generated secret "
        "in backend/.env"
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = int(
    os.getenv("JWT_ACCESS_TOKEN_MINUTES", "30")
)

password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hasher.verify(password, hashed_password)


def create_access_token(user_id: int) -> tuple[str, str, datetime]:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    token_id = str(uuid4())

    payload = {
        "sub": str(user_id),
        "jti": token_id,
        "iat": now,
        "exp": expires_at,
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, token_id, expires_at


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
        options={"require": ["sub", "jti", "iat", "exp"]},
    )