import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "customer_service.settings")
django.setup()

from app.models import Customer

if not Customer.objects.exists():
    Customer.objects.bulk_create([
        Customer(name="Alice Nguyen", email="alice@example.com"),
        Customer(name="Bob Tran", email="bob@example.com"),
    ])
    print("✅ Sample customers inserted.")
else:
    print("ℹ️ Customers already exist, skipping seed.")
