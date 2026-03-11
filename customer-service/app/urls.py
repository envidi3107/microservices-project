from django.urls import path
from . import views

urlpatterns = [
    path('', views.CustomerListCreate.as_view(), name='customer-list-create'),
]
