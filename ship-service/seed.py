import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ship_service.settings")
django.setup()

from app.models import Book

if not Book.objects.exists():
    Book.objects.bulk_create([
        Book(title="The Pragmatic Programmer", author="Andrew Hunt", price=49.99, stock=12),
        Book(title="Clean Code", author="Robert C. Martin", price=39.99, stock=8),
        Book(title="Design Patterns", author="Gang of Four", price=54.99, stock=5),
        Book(title="Introduction to Algorithms", author="Cormen et al.", price=79.99, stock=3),
        Book(title="The Mythical Man-Month", author="Fred Brooks", price=29.99, stock=15),
        Book(title="You Don't Know JS", author="Kyle Simpson", price=34.99, stock=20),
    ])
    print("✅ Sample books inserted.")
else:
    print("ℹ️ Books already exist, skipping seed.")
