import logging
import os
import requests

logger = logging.getLogger(__name__)

PAY_SERVICE_URL = os.environ.get("PAY_SERVICE_URL", "http://pay-service:8000")
SHIP_SERVICE_URL = os.environ.get("SHIP_SERVICE_URL", "http://ship-service:8000")


class OrderSagaOrchestrator:
    """
    Orchestration-based Saga coordinator for order creation.

    Steps:
        1. Order is already saved as PENDING (done in view before calling this)
        2. reserve_payment  → POST /payments/reserve/
        3. reserve_shipping → POST /shipments/reserve/
        4. Confirm order    → PATCH order.status = CONFIRMED

    Compensation (on any failure):
        - Cancel payment   → POST /payments/<order_id>/cancel/
        - Cancel shipping  → POST /shipments/<order_id>/cancel/
        - Mark order FAILED
    """

    def execute(self, order) -> bool:
        """
        Run the full Saga. Returns True on success, False on failure.
        Mutates order.status in-place.
        """
        payment_reserved = False
        shipping_reserved = False

        logger.info(f"[SAGA] Starting saga for order_id={order.id}")

        # ── Step 2: Reserve Payment ──────────────────────────────────────────
        try:
            resp = requests.post(
                f"{PAY_SERVICE_URL}/payments/reserve/",
                json={
                    "order_id": order.id,
                    "amount": str(order.total_price),
                    "payment_method": order.payment_method,
                },
                timeout=5,
            )
            if resp.status_code in (200, 201):
                payment_reserved = True
                logger.info(f"[SAGA] Payment reserved for order_id={order.id}")
            else:
                raise Exception(f"Payment reservation failed: {resp.status_code} {resp.text}")
        except Exception as e:
            logger.error(f"[SAGA] Payment step failed: {e}")
            self._compensate(order, payment_reserved=False, shipping_reserved=False)
            return False

        # ── Step 3: Reserve Shipping ─────────────────────────────────────────
        try:
            resp = requests.post(
                f"{SHIP_SERVICE_URL}/shipments/reserve/",
                json={
                    "order_id": order.id,
                    "address": order.address,
                    "shipping_method": order.shipping_method,
                },
                timeout=5,
            )
            if resp.status_code in (200, 201):
                shipping_reserved = True
                logger.info(f"[SAGA] Shipping reserved for order_id={order.id}")
            else:
                raise Exception(f"Shipping reservation failed: {resp.status_code} {resp.text}")
        except Exception as e:
            logger.error(f"[SAGA] Shipping step failed: {e}")
            self._compensate(order, payment_reserved=True, shipping_reserved=False)
            return False

        # ── Step 4: Confirm Order ─────────────────────────────────────────────
        order.status = "CONFIRMED"
        order.save()
        logger.info(f"[SAGA] Order {order.id} confirmed successfully.")
        return True

    def _compensate(self, order, payment_reserved: bool, shipping_reserved: bool):
        """Roll back whatever steps succeeded."""
        logger.warning(f"[SAGA] Compensating for order_id={order.id}")

        if payment_reserved:
            try:
                resp = requests.post(
                    f"{PAY_SERVICE_URL}/payments/{order.id}/cancel/",
                    timeout=5,
                )
                logger.info(f"[SAGA] Payment cancelled for order_id={order.id}: {resp.status_code}")
            except Exception as e:
                logger.error(f"[SAGA] Failed to cancel payment: {e}")

        if shipping_reserved:
            try:
                resp = requests.post(
                    f"{SHIP_SERVICE_URL}/shipments/{order.id}/cancel/",
                    timeout=5,
                )
                logger.info(f"[SAGA] Shipment cancelled for order_id={order.id}: {resp.status_code}")
            except Exception as e:
                logger.error(f"[SAGA] Failed to cancel shipment: {e}")

        order.status = "FAILED"
        order.save()
        logger.warning(f"[SAGA] Order {order.id} marked as FAILED.")
