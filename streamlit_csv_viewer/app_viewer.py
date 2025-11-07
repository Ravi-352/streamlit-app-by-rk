# app_viewer.py
import streamlit as st
import pandas as pd
import os
import re
from io import StringIO
import numpy
import plotly
import sklearn
import statsmodels
import joblib
import scipy
import shap
import tensorflow
import requests
import prometheus_client
import pkg_resources
import importlib
import yaml

packages = ["pandas", "numpy", "yaml", "streamlit", "plotly", "sklearn", "statsmodels", "joblib", "scipy", "shap", "tensorflow", "requests", "prometheus_client"]

def show_versions():
    st.write("### Library Versions")
    rows = []
    for p in packages:
        try:
            mod = importlib.import_module(p)
            ver = getattr(mod,"__version__", None)
            rows.append({"module": p, "version": ver})
        except Exception as e:
            #st.write(f"{p}: Error --> {type(e).__name__}: {e}")
            rows.append({"module": p, "version": f"NOT INSTALLED ({e})"})
    return rows

# --- Sidebar toggle state ---
if "show_versions" not in st.session_state:
    st.session_state.show_versions = False

def toggle_versions():
    st.session_state.show_versions = not st.session_state.show_versions

# --- Toggle button ---
st.sidebar.button(
    "Hide Import Module Versions" if st.session_state.show_versions else "Show Import Module Versions",
    on_click=toggle_versions,
)

# --- Sidebar content ---
with st.sidebar:
    if st.session_state.show_versions:
        st.markdown("### Library Versions")
        data = show_versions()
        st.table(data)



    
st.set_page_config(page_title="CSV Viewer", layout="wide")

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

st.title("CSV Inspector / Viewer")
st.write("Upload a CSV or pick one from the server `data/` folder to inspect, filter and download.")



# Option to pick server-side file
server_files = sorted([f for f in os.listdir(DATA_DIR) if f.lower().endswith(".csv")])
choice = st.radio("Load CSV from:", ("Upload file", "Choose from server `data/`"), index=1 if server_files else 0)

# Initialize session_state to store uploaded file content
if "uploaded_df" not in st.session_state:
    st.session_state.uploaded_df = None

df = None
if choice == "Upload file":
    uploaded = st.file_uploader("Upload CSV", type="csv")
    if uploaded is not None:
        # Save in session_state
        st.session_state.uploaded_df = pd.read_csv(uploaded)

    df = st.session_state.uploaded_df
else:
    if server_files:
        sel = st.selectbox("Select file", server_files)
        if sel:
            df = pd.read_csv(os.path.join(DATA_DIR, sel))
    else:
        st.info("No CSVs found in `data/`. Use the generator to create one or upload a file.")

if df is None:
    st.stop()

st.markdown("## Preview & Basic Info")
st.write(f"Rows: **{len(df)}**, Columns: **{len(df.columns)}**")
st.dataframe(df.head(20))

# Normalise column names
df.columns = [c.strip() for c in df.columns]

# Useful column detections
cols = df.columns.tolist()
has_ip = any(re.search(r"ip", c, re.I) for c in cols)
ip_col_candidates = [c for c in cols if re.search(r"ip", c, re.I)]
server_col = next((c for c in cols if re.search(r"server", c, re.I)), None)
app_col = next((c for c in cols if re.search(r"app", c, re.I)), None)
dc_col = next((c for c in cols if re.search(r"dc|datacenter|datacentre", c, re.I)), None)

st.markdown("## Quick Filters")
col_to_filter = st.selectbox("Filter column", options=["-- none --"] + cols)
filter_val = None
if col_to_filter and col_to_filter != "-- none --":
    unique_vals = df[col_to_filter].dropna().unique().tolist()
    if len(unique_vals) <= 50:
        filter_val = st.multiselect("Pick values to include (empty = all)", options=sorted(map(str, unique_vals)))
    else:
        text = st.text_input("Substring match (type to filter)")
        filter_val = text

# Apply filters
df_filtered = df.copy()
if col_to_filter and col_to_filter != "-- none --" and filter_val:
    if isinstance(filter_val, list):
        df_filtered = df_filtered[df_filtered[col_to_filter].astype(str).isin(filter_val)]
    else:
        df_filtered = df_filtered[df_filtered[col_to_filter].astype(str).str.contains(filter_val, case=False, na=False)]

st.markdown("### Filtered preview")
st.write(f"Showing {len(df_filtered)} rows after filter.")
st.dataframe(df_filtered.head(200))

# IP validation and summary
if ip_col_candidates:
    ip_col = ip_col_candidates[0]  # use first ip-like column
    st.markdown(f"## IP checks (using column `{ip_col}`)")
    import ipaddress
    def valid_ipv4(x):
        try:
            ipaddress.IPv4Address(str(x))
            return True
        except Exception:
            return False

    df_filtered["_ip_valid"] = df_filtered[ip_col].apply(valid_ipv4)
    valid_count = df_filtered["_ip_valid"].sum()
    st.write(f"Valid IPv4: **{valid_count}** / **{len(df_filtered)}**")
    st.dataframe(df_filtered[[ip_col, "_ip_valid"]].head(50))

# Aggregations
st.markdown("## Aggregations / Grouping")
group_cols = []
if app_col:
    group_cols.append(app_col)
if dc_col:
    group_cols.append(dc_col)
if server_col:
    group_cols.append(server_col)

if group_cols:
    grouping = st.multiselect("Group by columns", options=group_cols, default=group_cols[:2])
    if grouping:
        grp = df_filtered.groupby(grouping).size().reset_index(name="count").sort_values("count", ascending=False)
        st.dataframe(grp.head(200))
        st.download_button("Download group counts (CSV)", grp.to_csv(index=False).encode("utf-8"), file_name="group_counts.csv", mime="text/csv")

# Search rows
st.markdown("## Search rows (substring across all columns)")
search_term = st.text_input("Search term (case-insensitive)")
if search_term:
    mask = df_filtered.apply(lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(), axis=1)
    results = df_filtered[mask]
    st.write(f"Found {len(results)} matching rows")
    st.dataframe(results.head(200))
    st.download_button("Download search results (CSV)", results.to_csv(index=False).encode("utf-8"), file_name="search_results.csv", mime="text/csv")

# Download filtered dataframe
st.markdown("## Export")
csv_bytes = df_filtered.to_csv(index=False).encode("utf-8")
st.download_button("Download filtered CSV", csv_bytes, file_name="filtered_export.csv", mime="text/csv")

st.markdown("### Notes")
st.write("- If you plan to use server-side files, the viewer must run on the same machine/container that generated the CSVs (or you must mount shared storage).")
st.write("- For large CSVs (>100k rows) consider sampling or using chunked processing.")
