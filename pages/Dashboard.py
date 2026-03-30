import json
from pathlib import Path

import pandas as pd
import streamlit as st

st.session_state["current_page"] = "dashboard"

SESSIONS_FILE = Path("sessions.json")


def load_sessions() -> list[dict]:
    if not SESSIONS_FILE.exists():
        return []
    try:
        return json.loads(SESSIONS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("📊 Dashboard — Session History")

sessions = load_sessions()
if not sessions:
    st.info("No sessions yet. Play the Multiplication or Addition quiz to create session history.")
    st.stop()

df = pd.DataFrame(sessions)

if "timestamp_iso" in df.columns:
    df["timestamp_iso"] = pd.to_datetime(df["timestamp_iso"], errors="coerce")
    df = df.sort_values("timestamp_iso", ascending=False)

# Summary cards
col1, col2, col3, col4 = st.columns(4)

total_sessions = len(df)
avg_score = df["score"].mean() if "score" in df.columns else 0
avg_accuracy = df["accuracy_pct"].mean() if "accuracy_pct" in df.columns else 0
avg_speed = df["speed_q_per_min"].mean() if "speed_q_per_min" in df.columns else 0

col1.metric("Total sessions", f"{total_sessions}")
col2.metric("Avg score", f"{avg_score:.2f}")
col3.metric("Avg accuracy (%)", f"{avg_accuracy:.2f}")
col4.metric("Avg speed (q/min)", f"{avg_speed:.2f}")

st.divider()

# Filters
with st.expander("Filters", expanded=True):
    ops = sorted(df["operation"].dropna().unique().tolist()) if "operation" in df.columns else []
    selected_ops = st.multiselect("Operation", options=ops, default=ops)

    levels = sorted(df["level"].dropna().unique().tolist()) if "level" in df.columns else []
    selected_levels = st.multiselect("Level", options=levels, default=levels)

df_f = df.copy()
if selected_ops:
    df_f = df_f[df_f["operation"].isin(selected_ops)]
if selected_levels:
    df_f = df_f[df_f["level"].isin(selected_levels)]

st.subheader("Sessions")

show_cols = [
    "timestamp_iso",
    "operation",
    "level",
    "tables",
    "total_q",
    "score",
    "accuracy_pct",
    "avg_time_all_s",
    "avg_time_answered_s",
    "speed_q_per_min",
    "seconds_per_q",
]
show_cols = [c for c in show_cols if c in df_f.columns]

st.dataframe(df_f[show_cols], use_container_width=True, hide_index=True)

st.divider()

# Trends
st.subheader("Trends")
df_chart = df_f.dropna(subset=["timestamp_iso"]).copy()
df_chart = df_chart.sort_values("timestamp_iso")

c1, c2 = st.columns(2)
with c1:
    if "score" in df_chart.columns and len(df_chart) > 1:
        st.line_chart(df_chart.set_index("timestamp_iso")["score"], height=250)
    else:
        st.caption("Not enough data for score trend yet.")
with c2:
    if "speed_q_per_min" in df_chart.columns and len(df_chart) > 1:
        st.line_chart(df_chart.set_index("timestamp_iso")["speed_q_per_min"], height=250)
    else:
        st.caption("Not enough data for speed trend yet.")

st.divider()

if st.button("🗑️ Clear ALL session history (sessions.json)"):
    SESSIONS_FILE.write_text("[]", encoding="utf-8")
    st.success("Cleared session history.")
    st.rerun()
