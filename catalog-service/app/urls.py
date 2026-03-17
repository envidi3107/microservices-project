from django.urls import path
from . import views

urlpatterns = [
    path('', views.CatalogListCreate.as_view(), name='catalog-list-create'),
    path('<int:pk>/', views.CatalogDetail.as_view(), name='catalog-detail'),
]
