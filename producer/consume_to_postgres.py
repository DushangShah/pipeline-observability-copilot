import json
import psycopg2
from confluent_kafka import Consumer

conn = psycopg2.connect(
    host="localhost", port=5433, dbname="pipeline_db", user="pipeline", password="pipeline"
)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS raw_orders (
    order_id BIGINT,
    product TEXT,
    price NUMERIC,
    quantity INT,
    is_refund BOOLEAN,
    event_time TIMESTAMPTZ
);
""")
conn.commit()

consumer = Consumer({
    "bootstrap.servers": "localhost:9092",
    "group.id": "pg-writer",
    "auto.offset.reset": "earliest",
})
consumer.subscribe(["orders"])

print("Listening for orders...")
while True:
    msg = consumer.poll(1.0)
    if msg is None or msg.error():
        continue
    order = json.loads(msg.value())
    cur.execute(
        """INSERT INTO raw_orders (order_id, product, price, quantity, is_refund, event_time)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (order["order_id"], order["product"], order["price"],
         order["quantity"], order["is_refund"], order["event_time"]),
    )
    conn.commit()