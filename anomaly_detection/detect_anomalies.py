import pandas as pd
import psycopg2

conn = psycopg2.connect(
    host="localhost", port=5433, dbname="pipeline_db", user="pipeline", password="pipeline"
)

df = pd.read_sql("SELECT * FROM orders_per_minute ORDER BY event_minute", conn)

df["rolling_mean"] = df["order_count"].rolling(10, min_periods=3).mean()
df["rolling_std"] = df["order_count"].rolling(10, min_periods=3).std()
df["z_score"] = (df["order_count"] - df["rolling_mean"]) / df["rolling_std"]

anomalies = df[df["z_score"].abs() > 2.5]

if not anomalies.empty:
    print("⚠️ Anomalies detected:")
    print(anomalies[["event_minute", "order_count", "z_score"]])
else:
    print("No anomalies detected.")

cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS detected_anomalies (
    event_minute TIMESTAMPTZ,
    order_count INT,
    z_score NUMERIC
);
""")
for _, row in anomalies.iterrows():
    cur.execute(
        "INSERT INTO detected_anomalies (event_minute, order_count, z_score) VALUES (%s, %s, %s)",
        (row["event_minute"], row["order_count"], row["z_score"]),
    )
conn.commit()