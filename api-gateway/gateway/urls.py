from django.urls import path
from .views import book_list, view_cart, add_to_cart

urlpatterns = [
    path("books/", book_list, name="book_list"),
    path("cart/<int:customer_id>/", view_cart, name="view_cart"),
    path("cart/add/", add_to_cart, name="add_to_cart"),
]
