from django.urls import path
from . import views

urlpatterns = [
    path('orders/', views.OrderListCreate.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', views.OrderDetail.as_view(), name='order-detail'),
    path('health/', views.HealthView.as_view(), name='health'),
    path('metrics/', views.MetricsView.as_view(), name='metrics'),
]
