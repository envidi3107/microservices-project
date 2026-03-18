from django.urls import path
from . import views

urlpatterns = [
    path('payments/', views.PaymentListCreate.as_view(), name='payment-list-create'),
    path('payments/<int:pk>/', views.PaymentDetail.as_view(), name='payment-detail'),
    path('payments/reserve/', views.PaymentReserveView.as_view(), name='payment-reserve'),
    path('payments/<int:order_id>/cancel/', views.PaymentCancelView.as_view(), name='payment-cancel'),
    path('health/', views.HealthView.as_view(), name='health'),
    path('metrics/', views.MetricsView.as_view(), name='metrics'),
]
