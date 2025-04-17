from kafka import KafkaProducer
import json

from config import KAFKA_BROKER_URLS

_producer = None

def producer():
    global _producer
    if _producer is not None:
        return _producer
    _producer =KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URLS,
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )
    return _producer



if __name__ == "__main__":
    # # 假設 telegram_group_id 代表某個群組或用戶的唯一標識
    telegram_group_id = 'group_123'
    message = {"text": "Hello from Telegram!", "source": "client1"}

    # 指定 key 保證消息分到相同分區
    producer().send('telegram_topic', key=telegram_group_id.encode('utf-8'), value=message)
    producer().flush()
    print("Message sent to Kafka topic.")