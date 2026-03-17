from django.urls import path
from .views import book_list, view_cart, add_to_cart, dashboard, register_customer, staff_books, update_cart_item, checkout_view, book_detail, index

urlpatterns = [
    path("", index, name="index"),
    path("books/", book_list, name="book_list"),
    path("books/<int:book_id>/", book_detail, name="book_detail"),
    path("cart/<int:customer_id>/", view_cart, name="view_cart"),
    path("cart/add/", add_to_cart, name="add_to_cart"),
    path("cart/update/<int:item_id>/", update_cart_item, name="update_cart_item"),
    path("checkout/<int:customer_id>/", checkout_view, name="checkout"),
    path("dashboard/", dashboard, name="dashboard"),
    path("register/", register_customer, name="register_customer"),
    path("staff/books/", staff_books, name="staff_books"),
]
