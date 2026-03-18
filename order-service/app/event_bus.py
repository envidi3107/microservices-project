import json
import logging
import threading
import os

logger = logging.getLogger(__name__)

RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
EXCHANGE_NAME = "bookstore_events"


def _get_connection():
    import pika
    params = pika.URLParameters(RABBITMQ_URL)
    params.heartbeat = 30
    return pika.BlockingConnection(params)


def publish_event(event_type: str, payload: dict):
    """
    Publish an event to the 'bookstore_events' fanout exchange.
    Fire-and-forget; errors are logged but not raised.
    """
    try:
        connection = _get_connection()
        channel = connection.channel()
        channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic", durable=True)

        message = json.dumps({"event": event_type, "data": payload})
        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=event_type,
            body=message,
            properties=__import__("pika").BasicProperties(
                delivery_mode=2,  # persistent
                content_type="application/json",
            ),
        )
        connection.close()
        logger.info(f"[EVENT BUS] Published '{event_type}': {payload}")
    except Exception as e:
        logger.error(f"[EVENT BUS] Failed to publish '{event_type}': {e}")
