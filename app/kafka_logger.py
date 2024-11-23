import json
import traceback

from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic

from config import BOOTSTRAP_SERVERS, TOPIC_NAME, BATCH_SIZE

admin_client = KafkaAdminClient(bootstrap_servers=BOOTSTRAP_SERVERS, client_id='client-for-topic')
new_topic = NewTopic(name=TOPIC_NAME, num_partitions=1, replication_factor=1)

existing_topics = admin_client.list_topics()
if TOPIC_NAME not in existing_topics:
    try:
        admin_client.create_topics(new_topics=[new_topic], validate_only=False)
    except Exception:
        print(traceback.format_exc())
    finally:
        admin_client.close()


class KafkaBatchLogger:
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    topic = TOPIC_NAME
    batch_size = BATCH_SIZE
    buffer = []

    @classmethod
    def log(cls, message: dict):
        cls.buffer.append(message)
        if len(cls.buffer) >= cls.batch_size:
            cls._send()

    @classmethod
    def _send(cls):
        if not cls.buffer:
            return
        messages = cls.buffer
        cls.buffer = []

        for msg in messages:
            cls.producer.send(cls.topic, msg)
        cls.producer.flush()

    @classmethod
    def close(cls):
        cls._send()
        cls.producer.close()
