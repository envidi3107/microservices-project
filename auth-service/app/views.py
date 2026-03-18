import logging
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.hashers import check_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .utils import generate_token, verify_token
import jwt

logger = logging.getLogger(__name__)

# In-memory metrics counters (reset on container restart)
_metrics = {
    "total_registrations": 0,
    "total_logins": 0,
    "total_verifications": 0,
    "failed_logins": 0,
}


class RegisterView(APIView):
    """POST /register/ — Create a new user and return user info."""

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        if User.objects.filter(email=data["email"]).exists():
            return Response({"error": "Email already registered."}, status=status.HTTP_409_CONFLICT)

        user = User(email=data["email"], role=data.get("role", "user"))
        user.set_password(data["password"])
        user.save()

        _metrics["total_registrations"] += 1
        logger.info(f"[AUTH] New user registered: {user.email} (role={user.role})")

        return Response(
            {"id": user.id, "email": user.email, "role": user.role},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """POST /login/ — Authenticate user, return JWT token."""

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            _metrics["failed_logins"] += 1
            return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        if not check_password(data["password"], user.password):
            _metrics["failed_logins"] += 1
            return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({"error": "Account is inactive."}, status=status.HTTP_403_FORBIDDEN)

        token = generate_token(user.id, user.role)
        _metrics["total_logins"] += 1
        logger.info(f"[AUTH] User logged in: {user.email}")

        return Response(
            {"token": token, "user_id": user.id, "role": user.role},
            status=status.HTTP_200_OK,
        )


class VerifyTokenView(APIView):
    """
    POST /verify-token/ — Internal endpoint used by API Gateway to validate tokens.
    Returns 200 with payload on success, 401 on failure.
    """

    def post(self, request):
        token = request.data.get("token", "")
        if not token:
            return Response({"error": "Token required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = verify_token(token)
            _metrics["total_verifications"] += 1
            return Response({"valid": True, "user_id": payload["user_id"], "role": payload["role"]})
        except jwt.ExpiredSignatureError:
            return Response({"error": "Token expired."}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({"error": "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED)


class HealthView(APIView):
    """GET /health/ — Liveness probe."""

    def get(self, request):
        try:
            User.objects.count()  # Quick DB check
            db_status = "ok"
        except Exception:
            db_status = "error"
        return Response({"status": "ok", "service": "auth-service", "database": db_status})


class MetricsView(APIView):
    """GET /metrics/ — Simple counter metrics."""

    def get(self, request):
        return Response({
            "service": "auth-service",
            "total_users": User.objects.count(),
            **_metrics,
        })
