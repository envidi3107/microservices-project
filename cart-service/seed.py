import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cart_service.settings")
django.setup()

from app.models import Cart, CartItem

if not Cart.objects.exists():
    cart1 = Cart.objects.create(customer_id=1)
    cart2 = Cart.objects.create(customer_id=2)
    CartItem.objects.bulk_create([
        CartItem(cart=cart1, book_id=1, quantity=2),
        CartItem(cart=cart1, book_id=3, quantity=1),
        CartItem(cart=cart2, book_id=2, quantity=3),
    ])
    print("✅ Sample carts and items inserted.")
else:
    print("ℹ️ Carts already exist, skipping seed.")
