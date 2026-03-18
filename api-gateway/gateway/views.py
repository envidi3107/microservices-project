from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import os
import requests
import logging
import time

logger = logging.getLogger(__name__)

in_docker = os.environ.get("RUNNING_IN_DOCKER", False) or os.path.exists('/.dockerenv')

if in_docker:
    BOOK_SERVICE_URL = os.environ.get("BOOK_SERVICE_URL", "http://book-service:8000")
    CART_SERVICE_URL = os.environ.get("CART_SERVICE_URL", "http://cart-service:8000")
    CUSTOMER_SERVICE_URL = os.environ.get("CUSTOMER_SERVICE_URL", "http://customer-service:8000")
    ORDER_SERVICE_URL = os.environ.get("ORDER_SERVICE_URL", "http://order-service:8000")
    COMMENT_RATE_SERVICE_URL = os.environ.get("COMMENT_RATE_SERVICE_URL", "http://comment-rate-service:8000")
    STAFF_SERVICE_URL = os.environ.get("STAFF_SERVICE_URL", "http://staff-service:8000")
    AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://auth-service:8000")
else:
    BOOK_SERVICE_URL = os.environ.get("BOOK_SERVICE_URL", "http://localhost:8002")
    CART_SERVICE_URL = os.environ.get("CART_SERVICE_URL", "http://localhost:8003")
    CUSTOMER_SERVICE_URL = os.environ.get("CUSTOMER_SERVICE_URL", "http://localhost:8001")
    ORDER_SERVICE_URL = os.environ.get("ORDER_SERVICE_URL", "http://localhost:8007")
    COMMENT_RATE_SERVICE_URL = os.environ.get("COMMENT_RATE_SERVICE_URL", "http://localhost:8010")
    STAFF_SERVICE_URL = os.environ.get("STAFF_SERVICE_URL", "http://localhost:8004")
    AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://localhost:8012")

# Simple in-memory request counter for /metrics
_metrics = {"total_requests": 0, "total_errors": 0}


DEFAULT_CUSTOMER_ID = 1

def index(request):
    return render(request, "index.html")

def checkout_view(request, customer_id):
    # Fetch cart details to calculate total
    r = requests.get(f"{CART_SERVICE_URL}/carts/{customer_id}/")
    items = r.json() if r.ok else []

    books_resp = requests.get(f"{BOOK_SERVICE_URL}/books/")
    books_by_id = {}
    if books_resp.ok:
        books_by_id = {b["id"]: b for b in books_resp.json()}

    total = 0
    for item in items:
        item["book"] = books_by_id.get(item["book_id"], {})
        price = item["book"].get("price", 0)
        item["subtotal"] = round(float(price) * item["quantity"], 2)
        total += item["subtotal"]

    if request.method == "POST":
        address = request.POST.get("address")
        payment_method = request.POST.get("payment_method")
        shipping_method = request.POST.get("shipping_method")
        
        # Call order service to create order, pay, and ship
        order_data = {
            "customer_id": customer_id,
            "total_price": total,
            "address": address,
            "payment_method": payment_method,
            "shipping_method": shipping_method
        }
        resp = requests.post(f"{ORDER_SERVICE_URL}/orders/", json=order_data)
        
        if resp.ok:
            # Clear cart items logic normally happens here or in order-service. 
            # We will just show a success message.
            return render(request, "checkout.html", {
                "items": items, "customer_id": customer_id, "total": total,
                "message": "Order successfully placed! Payment and Shipping initiated.",
                "message_type": "success"
            })
        else:
            return render(request, "checkout.html", {
                "items": items, "customer_id": customer_id, "total": total,
                "message": "Failed to place order.",
                "message_type": "error"
            })

    return render(request, "checkout.html", {"items": items, "customer_id": customer_id, "total": round(total, 2)})

@require_http_methods(["GET", "POST"])
def register_customer(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        
        # Call customer-service to create user (which also creates the cart)
        resp = requests.post(f"{CUSTOMER_SERVICE_URL}/", json={"name": name, "email": email})
        
        if resp.ok:
            data = resp.json()
            return render(request, "register.html", {"message": f"Successfully registered! Your Customer ID is {data.get('id')}.", "message_type": "success"})
        else:
            return render(request, "register.html", {"message": "Email already exists or invalid data.", "message_type": "error"})
            
    return render(request, "register.html")



@require_http_methods(["GET", "POST"])
def book_detail(request, book_id):
    message = None
    message_type = None
    customer_id = request.POST.get("customer_id", DEFAULT_CUSTOMER_ID)

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")
        
        resp = requests.post(f"{COMMENT_RATE_SERVICE_URL}/reviews/", json={
            "book_id": book_id,
            "customer_id": customer_id,
            "rating": int(rating),
            "comment": comment
        })
        
        if resp.ok:
            message = "Review submitted successfully!"
            message_type = "success"
        else:
            message = "Failed to submit review."
            message_type = "error"

    # Fetch book details
    b_resp = requests.get(f"{BOOK_SERVICE_URL}/books/{book_id}/")
    book = b_resp.json() if b_resp.ok else None
    
    if not book:
        return redirect("/books/")

    # Fetch reviews
    r_resp = requests.get(f"{COMMENT_RATE_SERVICE_URL}/reviews/")
    all_reviews = r_resp.json() if r_resp.ok else []
    
    # Filter reviews for this book
    reviews = [r for r in all_reviews if r.get("book_id") == book_id]

    return render(request, "book_detail.html", {
        "book": book,
        "reviews": reviews,
        "message": message,
        "message_type": message_type
    })

@require_http_methods(["GET", "POST"])
def staff_books(request):
    message = None
    message_type = None

    if request.method == "POST":
        action = request.POST.get("action")
        
        if action == "create":
            data = {
                "title": request.POST.get("title"),
                "author": request.POST.get("author"),
                "price": request.POST.get("price"),
                "stock": request.POST.get("stock"),
            }
            resp = requests.post(f"{BOOK_SERVICE_URL}/books/", json=data)
            if resp.ok:
                message = "Book added successfully!"
                message_type = "success"
            else:
                message = "Failed to add book. Valid data required."
                message_type = "error"
                
        elif action == "delete":
            book_id = request.POST.get("book_id")
            resp = requests.delete(f"{BOOK_SERVICE_URL}/books/{book_id}/")
            if resp.ok or resp.status_code == 204:
                message = "Book deleted successfully!"
                message_type = "success"
            else:
                message = "Failed to delete book."
                message_type = "error"

    r = requests.get(f"{BOOK_SERVICE_URL}/books/")
    books = r.json() if r.ok else []
    
    return render(request, "staff_books.html", {
        "books": books,
        "message": message,
        "message_type": message_type
    })

def book_list(request):
    r = requests.get(f"{BOOK_SERVICE_URL}/books/")
    books = r.json() if r.ok else []
    return render(request, "books.html", {"books": books})


def view_cart(request, customer_id):
    r = requests.get(f"{CART_SERVICE_URL}/carts/{customer_id}/")
    items = r.json() if r.ok else []

    # Enrich items with book details
    books_resp = requests.get(f"{BOOK_SERVICE_URL}/books/")
    books_by_id = {}
    if books_resp.ok:
        books_by_id = {b["id"]: b for b in books_resp.json()}

    for item in items:
        item["book"] = books_by_id.get(item["book_id"], {})
        price = item["book"].get("price")
        if price:
            item["subtotal"] = round(float(price) * item["quantity"], 2)

    return render(request, "cart.html", {"items": items[::-1], "customer_id": customer_id})


@require_POST
def add_to_cart(request):
    book_id = int(request.POST.get("book_id"))
    quantity = int(request.POST.get("quantity", 1))
    customer_id = int(request.POST.get("customer_id", DEFAULT_CUSTOMER_ID))

    # Get or create cart for this customer
    cart_resp = requests.post(f"{CART_SERVICE_URL}/carts/", json={"customer_id": customer_id})
    cart_id = cart_resp.json().get("id")

    if cart_id:
        requests.post(f"{CART_SERVICE_URL}/carts/items/", json={"cart": cart_id, "book_id": book_id, "quantity": quantity})

    return redirect(f"/cart/{customer_id}/")
    
@require_POST
def update_cart_item(request, item_id):
    action = request.POST.get("action")
    customer_id = int(request.POST.get("customer_id", DEFAULT_CUSTOMER_ID))
    
    if action == "update":
        quantity = int(request.POST.get("quantity", 1))
        requests.put(f"{CART_SERVICE_URL}/carts/items/{item_id}/", json={"quantity": quantity})
    elif action == "delete":
        requests.delete(f"{CART_SERVICE_URL}/carts/items/{item_id}/")
        
    return redirect(f"/cart/{customer_id}/")

def dashboard(request):
    data = {
        "revenue": 0.0,
        "orders": [],
        "customers": [],
        "staff": []
    }
    
    try:
        r_orders = requests.get(f"{ORDER_SERVICE_URL}/orders/", timeout=2.0)
        data["orders"] = r_orders.json() if r_orders.ok else []
        for o in data["orders"]:
            data["revenue"] += float(o.get("total_price", 0))
    except:
        pass
        
    try:
        r_cust = requests.get(f"{CUSTOMER_SERVICE_URL}/", timeout=2.0)
        data["customers"] = r_cust.json() if r_cust.ok else []
    except:
        pass
        
    try:
        r_staff = requests.get(f"{STAFF_SERVICE_URL}/staff/", timeout=2.0)
        data["staff"] = r_staff.json() if r_staff.ok else []
    except:
        pass
        
    data["revenue"] = round(data["revenue"], 2)
    return render(request, "dashboard.html", {"data": data})


# ─────────────── API ENDPOINTS (JWT-protected) ───────────────

@csrf_exempt
def api_auth_login(request):
    """POST /api/auth/login/ — Proxy to auth-service login (no JWT required)."""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        resp = requests.post(f"{AUTH_SERVICE_URL}/login/", json=__import__('json').loads(request.body), timeout=5)
        return JsonResponse(resp.json(), status=resp.status_code)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=503)


@csrf_exempt
def api_auth_register(request):
    """POST /api/auth/register/ — Proxy to auth-service register (no JWT required)."""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        resp = requests.post(f"{AUTH_SERVICE_URL}/register/", json=__import__('json').loads(request.body), timeout=5)
        return JsonResponse(resp.json(), status=resp.status_code)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=503)


@csrf_exempt
def api_orders(request):
    """
    GET/POST /api/orders/ — JWT-protected order creation proxy.
    JWT validation is handled by JWTMiddleware before reaching this view.
    """
    import json
    try:
        if request.method == "GET":
            resp = requests.get(f"{ORDER_SERVICE_URL}/orders/", timeout=5)
        elif request.method == "POST":
            data = json.loads(request.body)
            # Attach authenticated user_id from JWT if not explicitly provided
            if hasattr(request, 'user_id') and request.user_id and 'customer_id' not in data:
                data['customer_id'] = request.user_id
            resp = requests.post(f"{ORDER_SERVICE_URL}/orders/", json=data, timeout=15)
        else:
            return JsonResponse({"error": "Method not allowed"}, status=405)
        return JsonResponse(resp.json(), status=resp.status_code, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=503)


def health_view(request):
    """GET /health/ — Gateway health check."""
    return JsonResponse({"status": "ok", "service": "api-gateway"})


def metrics_view(request):
    """GET /metrics/ — Simple gateway metrics."""
    return JsonResponse({
        "service": "api-gateway",
        **_metrics,
    })
