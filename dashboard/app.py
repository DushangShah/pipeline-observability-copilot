import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "nl_interface"))

import streamlit as st
import pandas as pd
import psycopg2
from ask import ask

conn = psycopg2.connect(host="localhost", port=5433, dbname="pipeline_db", user="pipeline", password="pipeline")

st.set_page_config(page_title="Pipeline Observability Copilot", page_icon="📈")
st.title("📈 Pipeline Observability Copilot")

df = pd.read_sql("SELECT * FROM orders_per_minute ORDER BY event_minute", conn)
st.subheader("Order volume over time")
st.line_chart(df.set_index("event_minute")["order_count"])

anomalies = pd.read_sql("SELECT * FROM detected_anomalies ORDER BY event_minute DESC", conn)
if not anomalies.empty:
    st.subheader("⚠️ Recent anomalies")
    st.dataframe(anomalies)
else:
    st.info("No anomalies detected yet.")

st.divider()
st.subheader("Ask about your pipeline")
question = st.text_input("e.g. 'Was there a drop in orders today?'")
if question:
    with st.spinner("Checking the data..."):
        st.write(ask(question))