from django.urls import path
from .views import RegisterView, LoginView, VerifyTokenView, HealthView, MetricsView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("verify-token/", VerifyTokenView.as_view(), name="verify-token"),
    path("health/", HealthView.as_view(), name="health"),
    path("metrics/", MetricsView.as_view(), name="metrics"),
]
