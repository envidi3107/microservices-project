from django.urls import path
from . import views

urlpatterns = [
    path('', views.CartCreate.as_view(), name='cart-create'),
    path('items/', views.AddCartItem.as_view(), name='cart-add-item'),
    path('items/<int:item_id>/', views.UpdateDeleteCartItem.as_view(), name='cart-update-delete-item'),
    path('<int:customer_id>/', views.ViewCart.as_view(), name='cart-view'),
]
