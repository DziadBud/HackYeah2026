import json
import uuid
from datetime import UTC, datetime

import pika

# delivery: at-least-once towards rag. durable queue, persistent messages and publisher
# confirms, so a returned publish means the broker has it. the consumer (rag) must be
# idempotent; /embed replaces all chunks of an innovation, so a redelivery is harmless
EMBED_REQUESTED = "innovation.embed_requested"


class RabbitEmbedPublisher:
    def __init__(self, url: str, queue: str) -> None:
        self._url = url
        self._queue = queue

    def publish_embed_requested(self, innovation_id: str, file_path: str) -> None:
        event = {
            "id": str(uuid.uuid4()),
            "type": EMBED_REQUESTED,
            "version": 1,
            "occurred_at": datetime.now(UTC).isoformat(),
            "innovation_id": innovation_id,
            "file_path": file_path,
        }
        # one connection per publish: admin uploads are rare, and it avoids sharing a
        # blocking connection across request threads
        connection = pika.BlockingConnection(pika.URLParameters(self._url))
        try:
            channel = connection.channel()
            channel.queue_declare(queue=self._queue, durable=True)
            channel.confirm_delivery()
            channel.basic_publish(
                exchange="",
                routing_key=self._queue,
                body=json.dumps(event).encode(),
                properties=pika.BasicProperties(
                    content_type="application/json",
                    delivery_mode=pika.DeliveryMode.Persistent,
                    message_id=event["id"],
                    type=EMBED_REQUESTED,
                ),
                mandatory=True,
            )
        finally:
            connection.close()
