import os

BOOTSTRAP_SERVERS: str = "kafka:9092"
TOPIC_NAME: str = "logs-topic"
BATCH_SIZE: int = 3

POSTGRES_DB: str = os.environ["POSTGRES_DB"]
POSTGRES_USER: str = os.environ["POSTGRES_USER"]
POSTGRES_PASSWORD: str = os.environ["POSTGRES_PASSWORD"]
POSTGRES_PORT: str = os.environ["POSTGRES_PORT"]
POSTGRES_HOST: str = os.environ["POSTGRES_HOST"]
