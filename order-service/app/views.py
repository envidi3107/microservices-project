import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from .serializers import OrderSerializer
from .saga_orchestrator import OrderSagaOrchestrator
from .event_bus import publish_event

logger = logging.getLogger(__name__)

_metrics = {"total_orders": 0, "confirmed_orders": 0, "failed_orders": 0}


class OrderListCreate(APIView):
    def get(self, request):
        orders = Order.objects.all().order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Step 1: Create order as PENDING
        order = serializer.save(status="PENDING")
        _metrics["total_orders"] += 1
        logger.info(f"[ORDER] Created order #{order.id} as PENDING for customer {order.customer_id}")

        # Steps 2-4: Run Saga (reserve payment → reserve shipping → confirm)
        orchestrator = OrderSagaOrchestrator()
        success = orchestrator.execute(order)

        # Refresh from DB after saga mutated status
        order.refresh_from_db()

        if success:
            _metrics["confirmed_orders"] += 1
            publish_event("order_confirmed", {
                "order_id": order.id,
                "customer_id": order.customer_id,
                "total_price": str(order.total_price),
                "status": order.status,
            })
        else:
            _metrics["failed_orders"] += 1
            publish_event("order_failed", {
                "order_id": order.id,
                "customer_id": order.customer_id,
                "reason": "Saga compensation triggered",
            })

        result_serializer = OrderSerializer(order)
        http_status = status.HTTP_201_CREATED if success else status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response(result_serializer.data, status=http_status)


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
        return Response(OrderSerializer(order).data)

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


class HealthView(APIView):
    def get(self, request):
        try:
            Order.objects.count()
            db_status = "ok"
        except Exception:
            db_status = "error"
        return Response({"status": "ok", "service": "order-service", "database": db_status})


class MetricsView(APIView):
    def get(self, request):
        return Response({
            "service": "order-service",
            "total_orders_in_db": Order.objects.count(),
            **_metrics,
        })
