import os
import logging
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Shipment
from .serializers import ShipmentSerializer

logger = logging.getLogger(__name__)

_metrics = {"total_reserves": 0, "total_cancellations": 0, "total_failures": 0}

FORCE_FAIL = os.environ.get("FORCE_FAIL", "false").lower() == "true"


class ShipmentListCreate(APIView):
    """GET /shipments/ — List all shipments."""

    def get(self, request):
        shipments = Shipment.objects.all().order_by("-created_at")
        serializer = ShipmentSerializer(shipments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ShipmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShipmentReserveView(APIView):
    """
    POST /shipments/reserve/
    Called by the Saga orchestrator (Step 3: Reserve Shipping).
    """

    def post(self, request):
        if FORCE_FAIL:
            _metrics["total_failures"] += 1
            logger.warning("[SHIP] FORCE_FAIL=true — simulating shipping failure!")
            return Response(
                {"error": "Shipping service is simulating a failure (FORCE_FAIL=true)"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        order_id = request.data.get("order_id")
        address = request.data.get("address", "")
        shipping_method = request.data.get("shipping_method", "Standard")

        if not order_id:
            return Response({"error": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        existing = Shipment.objects.filter(order_id=order_id).first()
        if existing:
            return Response(ShipmentSerializer(existing).data, status=status.HTTP_200_OK)

        tracking_number = f"TRACK-{uuid.uuid4().hex[:8].upper()}"
        shipment = Shipment.objects.create(
            order_id=order_id,
            address=address,
            shipping_method=shipping_method,
            tracking_number=tracking_number,
            status="RESERVED",
        )
        _metrics["total_reserves"] += 1
        logger.info(f"[SHIP] Reserved shipment for order_id={order_id}, tracking={tracking_number}")
        return Response(ShipmentSerializer(shipment).data, status=status.HTTP_201_CREATED)


class ShipmentCancelView(APIView):
    """
    POST /shipments/<order_id>/cancel/
    Called by the Saga orchestrator during compensation.
    """

    def post(self, request, order_id):
        try:
            shipment = Shipment.objects.get(order_id=order_id)
            shipment.status = "CANCELLED"
            shipment.save()
            _metrics["total_cancellations"] += 1
            logger.info(f"[SHIP] Cancelled shipment for order_id={order_id}")
            return Response({"status": "cancelled", "order_id": order_id})
        except Shipment.DoesNotExist:
            return Response({"status": "not_found", "order_id": order_id})


class ShipmentDetail(APIView):
    def get_object(self, pk):
        try:
            return Shipment.objects.get(pk=pk)
        except Shipment.DoesNotExist:
            return None

    def get(self, request, pk):
        shipment = self.get_object(pk)
        if shipment is None:
            return Response({"error": "Shipment not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(ShipmentSerializer(shipment).data)

    def delete(self, request, pk):
        shipment = self.get_object(pk)
        if shipment is None:
            return Response({"error": "Shipment not found"}, status=status.HTTP_404_NOT_FOUND)
        shipment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class HealthView(APIView):
    def get(self, request):
        try:
            Shipment.objects.count()
            db_status = "ok"
        except Exception:
            db_status = "error"
        return Response({
            "status": "ok",
            "service": "ship-service",
            "database": db_status,
            "force_fail": FORCE_FAIL,
        })


class MetricsView(APIView):
    def get(self, request):
        return Response({
            "service": "ship-service",
            "total_shipments_in_db": Shipment.objects.count(),
            **_metrics,
        })
