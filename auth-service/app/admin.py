from django.contrib import admin

admin.site.register(__import__("app.models", fromlist=["User"]).User)
