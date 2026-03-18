import time
import logging
import os
import jwt
from collections import defaultdict
from django.http import JsonResponse
from django.core.cache import cache

logger = logging.getLogger(__name__)

JWT_SECRET = os.environ.get("JWT_SECRET", "bookstore-super-secret-jwt-key-2024")

# Paths that do NOT require JWT authentication
OPEN_PATHS = {
    "/",
    "/books/",
    "/register/",
    "/health/",
    "/metrics/",
    "/api/auth/login/",
    "/api/auth/register/",
}


class JWTMiddleware:
    """
    Validates JWT tokens for all /api/ routes (excluding auth endpoints).
    Attaches request.user_id and request.user_role on success.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info

        # Only protect /api/ routes
        if path.startswith("/api/") and path not in OPEN_PATHS:
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
            if not auth_header.startswith("Bearer "):
                return JsonResponse(
                    {"error": "Authorization header missing or malformed. Expected: Bearer <token>"},
                    status=401,
                )
            token = auth_header[len("Bearer "):]
            try:
                payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
                request.user_id = payload.get("user_id")
                request.user_role = payload.get("role", "user")
            except jwt.ExpiredSignatureError:
                return JsonResponse({"error": "Token expired."}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({"error": "Invalid token."}, status=401)
        else:
            request.user_id = None
            request.user_role = None

        response = self.get_response(request)
        return response


class LoggingMiddleware:
    """
    Logs every request: method, path, status code, and duration.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration_ms = round((time.time() - start) * 1000, 2)
        logger.info(
            f"[GATEWAY] {request.method} {request.path} → {response.status_code} ({duration_ms}ms) "
            f"ip={self._get_ip(request)}"
        )
        return response

    def _get_ip(self, request):
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")


class RateLimitMiddleware:
    """
    Simple per-IP rate limiting: 100 requests/minute.
    Uses Django's cache backend (default: in-memory LocMemCache).
    """

    LIMIT = 100
    WINDOW = 60  # seconds

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self._get_ip(request)
        cache_key = f"ratelimit:{ip}"
        current = cache.get(cache_key, 0)

        if current >= self.LIMIT:
            logger.warning(f"[RATE LIMIT] IP {ip} exceeded {self.LIMIT} req/min")
            return JsonResponse(
                {"error": "Rate limit exceeded. Try again in a minute."},
                status=429,
            )

        # Increment counter; set TTL only on first hit
        if current == 0:
            cache.set(cache_key, 1, timeout=self.WINDOW)
        else:
            cache.incr(cache_key)

        return self.get_response(request)

    def _get_ip(self, request):
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")
