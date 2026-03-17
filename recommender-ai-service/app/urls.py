from django.urls import path
from . import views

urlpatterns = [
    path('', views.RecommendationListCreate.as_view(), name='recommendation-list-create'),
    path('<int:pk>/', views.RecommendationDetail.as_view(), name='recommendation-detail'),
]
