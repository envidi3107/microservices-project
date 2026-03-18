import json
import logging
import os
import pika
import django
import sys
import time

# Set up Django context
sys.path.append("/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ship_service.settings")
django.setup()

from app.models import Shipment

logger = logging.getLogger(__name__)

RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
EXCHANGE_NAME = "bookstore_events"
QUEUE_NAME = "shipping_queue"


def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        event = data.get("event")
        payload = data.get("data", {})

        if event == "order_created":
            logger.info(f"[SHIP CONSUMER] Received order_created for order_id={payload.get('order_id')}")
        elif event == "order_failed":
            logger.info(f"[SHIP CONSUMER] Received order_failed for order_id={payload.get('order_id')}")

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"[SHIP CONSUMER] Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def start_consuming():
    while True:
        try:
            params = pika.URLParameters(RABBITMQ_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()

            channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic", durable=True)
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key="#")

            logger.info("[SHIP CONSUMER] Connected to RabbitMQ. Waiting for messages...")
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            logger.warning("[SHIP CONSUMER] RabbitMQ not available yet. Retrying in 5s...")
            time.sleep(5)
        except Exception as e:
            logger.error(f"[SHIP CONSUMER] Unexpected error: {e}. Retrying in 5s...")
            time.sleep(5)


if __name__ == "__main__":
    start_consuming()
