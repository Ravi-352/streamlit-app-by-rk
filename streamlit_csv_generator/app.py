# app_generator.py
import streamlit as st
import pandas as pd
import random
import os
from datetime import datetime, timedelta
import ipaddress

st.set_page_config(page_title="CSV Generator", layout="centered")

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

st.title("Simulated CSV Generator")
st.write("Generate CSVs containing app, datacenter, server, env and IP data.")

# Inputs
n = st.number_input("Rows to generate", min_value=1, max_value=20000, value=200, step=1)
apps = st.text_area("App names (comma separated)", value="webapp,auth,api,worker,cache").strip()
dcs = st.text_area("Datacenters (comma separated)", value="us-east,us-west,eu-central,ap-south").strip()
start_ip = st.text_input("Base IPv4 (used to generate sequential IPs)", value="10.0.0.1")
envs = st.text_area("Environments (comma separated)", value="dev,qa,staging,prod").strip()
os_choices = st.text_area("OS choices (comma separated)", value="ubuntu,centos,windows").strip()

generate_btn = st.button("Generate CSV")

def next_ip(base_ip, offset):
    # produce deterministic ip by offset from base_ip
    try:
        ip = ipaddress.IPv4Address(base_ip) + offset
        return str(ip)
    except Exception:
        # fallback to random ip in 10.x.x.x
        return f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"

if generate_btn:
    app_list = [a.strip() for a in apps.split(",") if a.strip()]
    dc_list = [d.strip() for d in dcs.split(",") if d.strip()]
    env_list = [e.strip() for e in envs.split(",") if e.strip()]
    os_list = [o.strip() for o in os_choices.split(",") if o.strip()]

    rows = []
    now = datetime.utcnow()
    for i in range(int(n)):
        app_name = random.choice(app_list)
        dc = random.choice(dc_list)
        env = random.choice(env_list)
        os_name = random.choice(os_list)
        server_name = f"{app_name}-{dc}-srv{str(i+1).zfill(3)}"
        ip_addr = next_ip(start_ip, i)
        created_at = (now - timedelta(days=random.randint(0,365))).isoformat()
        rows.append({
            "app_name": app_name,
            "dc_name": dc,
            "server_name": server_name,
            "ip_address": ip_addr,
            "os": os_name,
            "environment": env,
            "created_at": created_at
        })

    df = pd.DataFrame(rows)
    filename = f"simulated_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.csv"
    filepath = os.path.join(DATA_DIR, filename)
    df.to_csv(filepath, index=False)

    st.success(f"CSV generated and saved to `{filepath}` — {len(df)} rows.")
    st.download_button("Download generated CSV", df.to_csv(index=False).encode("utf-8"), file_name=filename, mime="text/csv")
    st.write("Sample:")
    st.dataframe(df.head(15))
