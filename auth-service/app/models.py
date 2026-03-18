from django.db import models
from django.contrib.auth.hashers import make_password

ROLE_CHOICES = [
    ("user", "User"),
    ("admin", "Admin"),
]


class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="user")
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def __str__(self):
        return self.email
