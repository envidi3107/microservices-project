import os
import logging
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Payment
from .serializers import PaymentSerializer

logger = logging.getLogger(__name__)

_metrics = {"total_reserves": 0, "total_cancellations": 0, "total_failures": 0}

# Fault simulation flag — set FORCE_FAIL=true in docker-compose environment
FORCE_FAIL = os.environ.get("FORCE_FAIL", "false").lower() == "true"


class PaymentListCreate(APIView):
    """GET /payments/ — List all payments."""

    def get(self, request):
        payments = Payment.objects.all().order_by("-created_at")
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentReserveView(APIView):
    """
    POST /payments/reserve/
    Called by the Saga orchestrator (Step 2: Reserve Payment).
    Respects FORCE_FAIL env var for fault simulation.
    """

    def post(self, request):
        if FORCE_FAIL:
            _metrics["total_failures"] += 1
            logger.warning("[PAY] FORCE_FAIL=true — simulating payment failure!")
            return Response(
                {"error": "Payment service is simulating a failure (FORCE_FAIL=true)"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        order_id = request.data.get("order_id")
        amount = request.data.get("amount", 0)
        payment_method = request.data.get("payment_method", "Credit Card")

        if not order_id:
            return Response({"error": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Idempotency: check if already reserved
        existing = Payment.objects.filter(order_id=order_id).first()
        if existing:
            return Response(PaymentSerializer(existing).data, status=status.HTTP_200_OK)

        payment = Payment.objects.create(
            order_id=order_id,
            amount=amount,
            payment_method=payment_method,
            status="RESERVED",
        )
        _metrics["total_reserves"] += 1
        logger.info(f"[PAY] Reserved payment for order_id={order_id}")
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


class PaymentCancelView(APIView):
    """
    POST /payments/<order_id>/cancel/
    Called by the Saga orchestrator during compensation.
    """

    def post(self, request, order_id):
        try:
            payment = Payment.objects.get(order_id=order_id)
            payment.status = "CANCELLED"
            payment.save()
            _metrics["total_cancellations"] += 1
            logger.info(f"[PAY] Cancelled payment for order_id={order_id}")
            return Response({"status": "cancelled", "order_id": order_id})
        except Payment.DoesNotExist:
            # No payment to cancel — idempotent, return OK
            return Response({"status": "not_found", "order_id": order_id})


class PaymentDetail(APIView):
    def get_object(self, pk):
        try:
            return Payment.objects.get(pk=pk)
        except Payment.DoesNotExist:
            return None

    def get(self, request, pk):
        payment = self.get_object(pk)
        if payment is None:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(PaymentSerializer(payment).data)

    def delete(self, request, pk):
        payment = self.get_object(pk)
        if payment is None:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)
        payment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class HealthView(APIView):
    def get(self, request):
        try:
            Payment.objects.count()
            db_status = "ok"
        except Exception:
            db_status = "error"
        return Response({
            "status": "ok",
            "service": "pay-service",
            "database": db_status,
            "force_fail": FORCE_FAIL,
        })


class MetricsView(APIView):
    def get(self, request):
        return Response({
            "service": "pay-service",
            "total_payments_in_db": Payment.objects.count(),
            **_metrics,
        })
