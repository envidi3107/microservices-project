from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
import requests

BOOK_SERVICE_URL = "http://book-service:8000"
CART_SERVICE_URL = "http://cart-service:8000"

DEFAULT_CUSTOMER_ID = 1


def book_list(request):
    r = requests.get(f"{BOOK_SERVICE_URL}/books/")
    books = r.json() if r.ok else []
    return render(request, "books.html", {"books": books})


def view_cart(request, customer_id):
    r = requests.get(f"{CART_SERVICE_URL}/carts/{customer_id}/")
    items = r.json() if r.ok else []
    return render(request, "cart.html", {"items": items, "customer_id": customer_id})


@require_POST
def add_to_cart(request):
    book_id = int(request.POST.get("book_id"))
    quantity = int(request.POST.get("quantity", 1))
    customer_id = DEFAULT_CUSTOMER_ID

    # Get or create cart for this customer
    cart_resp = requests.post(
        f"{CART_SERVICE_URL}/carts/",
        json={"customer_id": customer_id}
    )
    cart_id = cart_resp.json().get("id")

    if cart_id:
        requests.post(
            f"{CART_SERVICE_URL}/carts/items/",
            json={"cart": cart_id, "book_id": book_id, "quantity": quantity},
        )

    return redirect(f"/cart/{customer_id}/")
