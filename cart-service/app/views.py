from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
import requests

BOOK_SERVICE_URL = "http://book-service:8000"


class CartCreate(APIView):
    def post(self, request):
        customer_id = request.data.get("customer_id")
        cart = Cart.objects.filter(customer_id=customer_id).first()
        if not cart:
            cart = Cart.objects.create(customer_id=customer_id)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class AddCartItem(APIView):
    def post(self, request):
        book_id = request.data.get("book_id")
        r = requests.get(f"{BOOK_SERVICE_URL}/books/")
        books = r.json()
        if not any(b["id"] == book_id for b in books):
            return Response({"error": "Book not found"}, status=404)
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class ViewCart(APIView):
    def get(self, request, customer_id):
        cart = Cart.objects.filter(customer_id=customer_id).first()
        if not cart:
            return Response([])
        items = CartItem.objects.filter(cart=cart)
        serializer = CartItemSerializer(items, many=True)
        return Response(serializer.data)

class UpdateDeleteCartItem(APIView):
    def put(self, request, item_id):
        item = CartItem.objects.filter(id=item_id).first()
        if not item:
            return Response({"error": "Item not found"}, status=404)
        quantity = request.data.get("quantity")
        if quantity is not None:
            item.quantity = quantity
            item.save()
            return Response(CartItemSerializer(item).data)
        return Response({"error": "Quantity required"}, status=400)

    def delete(self, request, item_id):
        item = CartItem.objects.filter(id=item_id).first()
        if not item:
            return Response({"error": "Item not found"}, status=404)
        item.delete()
        return Response(status=204)
