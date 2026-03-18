from django.urls import path
from . import views

urlpatterns = [
    path('shipments/', views.ShipmentListCreate.as_view(), name='shipment-list-create'),
    path('shipments/<int:pk>/', views.ShipmentDetail.as_view(), name='shipment-detail'),
    path('shipments/reserve/', views.ShipmentReserveView.as_view(), name='shipment-reserve'),
    path('shipments/<int:order_id>/cancel/', views.ShipmentCancelView.as_view(), name='shipment-cancel'),
    path('health/', views.HealthView.as_view(), name='health'),
    path('metrics/', views.MetricsView.as_view(), name='metrics'),
]
