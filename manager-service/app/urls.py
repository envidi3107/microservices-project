from django.urls import path
from . import views

urlpatterns = [
    path('', views.ManagerListCreate.as_view(), name='manager-list-create'),
    path('<int:pk>/', views.ManagerDetail.as_view(), name='manager-detail'),
]
