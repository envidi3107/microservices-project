from django.urls import path
from . import views

urlpatterns = [
    path('', views.StaffListCreate.as_view(), name='staff-list-create'),
    path('<int:pk>/', views.StaffDetail.as_view(), name='staff-detail'),
]
