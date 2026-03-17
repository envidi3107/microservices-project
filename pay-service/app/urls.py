from django.urls import path
from . import views

urlpatterns = [
    path('', views.PaymentListCreate.as_view(), name='payment-list-create'),
    path('<int:pk>/', views.PaymentDetail.as_view(), name='payment-detail'),
]
