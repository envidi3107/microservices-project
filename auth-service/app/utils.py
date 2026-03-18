import jwt
import datetime
from django.conf import settings


def generate_token(user_id: int, role: str) -> str:
    """Generate a signed JWT token valid for 24 hours."""
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        "iat": datetime.datetime.utcnow(),
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    # PyJWT >= 2.0 returns str directly; older versions return bytes
    return token if isinstance(token, str) else token.decode("utf-8")


def verify_token(token: str) -> dict:
    """
    Decode and verify a JWT token.
    Returns the payload dict on success.
    Raises jwt.ExpiredSignatureError or jwt.InvalidTokenError on failure.
    """
    return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
