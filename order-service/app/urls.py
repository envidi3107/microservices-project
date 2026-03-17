from django.urls import path
from . import views

urlpatterns = [
    path('', views.OrderListCreate.as_view(), name='order-list-create'),
    path('<int:pk>/', views.OrderDetail.as_view(), name='order-detail'),
]
