from django.urls import path
from . import views

urlpatterns = [
    path('', views.ShipmentListCreate.as_view(), name='shipment-list-create'),
    path('<int:pk>/', views.ShipmentDetail.as_view(), name='shipment-detail'),
]
