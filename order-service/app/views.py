from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from .serializers import OrderSerializer

import requests

PAY_SERVICE_URL = "http://pay-service:8000"
SHIP_SERVICE_URL = "http://ship-service:8000"

class OrderListCreate(APIView):
    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save(status="Placed")
            
            # Extract additional fields passed from gateway that are not in Order model
            payment_method = request.data.get("payment_method", "Credit Card")
            address = request.data.get("address", "Default Address")
            
            # 1. Trigger Payment
            try:
                requests.post(f"{PAY_SERVICE_URL}/payments/", json={
                    "order_id": order.id,
                    "amount": str(order.total_price),
                    "status": "Success", # auto success for demo
                }, timeout=3.0)
            except Exception as e:
                print("Payment service failed:", e)
            
            # 2. Trigger Shipment
            try:
                requests.post(f"{SHIP_SERVICE_URL}/shipments/", json={
                    "order_id": order.id,
                    "address": address,
                    "status": "Pending",
                }, timeout=3.0)
            except Exception as e:
                print("Shipment service failed:", e)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderDetail(APIView):
    def get_object(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return None

    def get(self, request, pk):
        order = self.get_object(pk)
        if order is None:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def put(self, request, pk):
        order = self.get_object(pk)
        if order is None:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        order = self.get_object(pk)
        if order is None:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
