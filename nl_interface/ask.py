import os
from dotenv import load_dotenv
load_dotenv()

import psycopg2
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-3.8-flash")

SCHEMA_CONTEXT = """
Table: orders_per_minute(event_minute timestamp, order_count int, revenue numeric, refund_count int)
Table: detected_anomalies(event_minute timestamp, order_count int, z_score numeric)
"""

def ask(question: str) -> str:
    sql_prompt = f"""You write PostgreSQL queries. Schema:
{SCHEMA_CONTEXT}
Return ONLY the SQL query, nothing else, no markdown formatting, no explanation, for this question: {question}"""

    sql_response = model.generate_content(sql_prompt)
    sql = sql_response.text.strip().strip("`").replace("sql\n", "").strip()

    conn = psycopg2.connect(host="localhost", port=5433, dbname="pipeline_db", user="pipeline", password="pipeline")
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()

    explain_prompt = f"Question: {question}\nSQL: {sql}\nResult: {rows}\nExplain the answer in plain English."
    explanation = model.generate_content(explain_prompt)

    return explanation.text

if __name__ == "__main__":
    print(ask("Was there anything unusual with order volume today?"))