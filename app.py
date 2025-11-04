# app.py
# Simple Streamlit UI with Prometheus metrics server


from prometheus_client import start_http_server, Counter
import streamlit as st
import threading
import time


REQUEST_COUNTER = Counter('streamlit_button_clicks_total', 'Total button clicks in Streamlit app')


# Start Prometheus HTTP server in a background thread
def start_metrics_server(port: int = 8000):
# start_http_server is blocking, so run in a daemon thread
start_http_server(port)


metrics_thread = threading.Thread(target=start_metrics_server, args=(8000,), daemon=True)
metrics_thread.start()


# Streamlit app UI
st.title("Sample Streamlit App with Prometheus Metrics")


if st.button("Click me"):
REQUEST_COUNTER.inc()
st.write("Thanks! Click recorded.")


st.write("Prometheus metrics available at port 8000 -> /metrics")
