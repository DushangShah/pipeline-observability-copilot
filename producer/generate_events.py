import json
import random
import time
from datetime import datetime, timezone
from confluent_kafka import Producer

producer = Producer({"bootstrap.servers": "localhost:9092"})

PRODUCTS = ["mug", "t-shirt", "notebook", "sticker-pack", "hoodie"]

def make_order():
    return {
        "order_id": random.randint(100000, 999999),
        "product": random.choice(PRODUCTS),
        "price": round(random.uniform(5, 60), 2),
        "quantity": random.randint(1, 3),
        "is_refund": random.random() < 0.05,
        "event_time": datetime.now(timezone.utc).isoformat(),
    }

def inject_anomaly_mode(base_rate):
    if random.random() < 0.01:
        return "drought", base_rate * 5
    if random.random() < 0.01:
        return "refund_spike", base_rate
    return "normal", base_rate

if __name__ == "__main__":
    base_sleep = 0.5
    while True:
        mode, sleep_time = inject_anomaly_mode(base_sleep)
        order = make_order()
        if mode == "refund_spike":
            order["is_refund"] = True
        producer.produce("orders", json.dumps(order).encode("utf-8"))
        producer.flush()
        print(f"[{mode}] sent order {order['order_id']}")
        time.sleep(sleep_time)