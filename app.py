# streamlit_app.py

import os, calendar
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
from tools import connections_df

# 1) Load env & build agent (you can drop the free-text part if you like)
load_dotenv()
from bot import build_agent
agent = build_agent(verbose=False)

# 2) Import your tool functions directly
from tools import top_companies, stale_connections

st.set_page_config(page_title="LinkedIn AI Agent", layout="wide")
st.title("🔗 LinkedIn AI Networking Agent")

# --- Sidebar: Pre-built Analytics ---
st.sidebar.header("Quick Analytics")

# 2a) Top Companies
if st.sidebar.button("Show Top 5 Companies"):
    st.subheader("Top 5 Companies in Your Network")
    data = top_companies(5)
    # render as a table
    df_top = pd.DataFrame.from_dict(data, orient="index", columns=["Count"])
    df_top.index.name = "Company"
    st.table(df_top)
    
# 2b) Save Jobs (with button)
if st.sidebar.button("Show Saved Jobs"):
    st.subheader("Your Saved Jobs")
    jobs_path = os.path.join("data", "saved_jobs.csv")
    try:
        df_jobs = pd.read_csv(jobs_path)
        st.dataframe(df_jobs)
    except FileNotFoundError:
        st.error(f"Could not find `{jobs_path}`. Make sure it exists.")

# 2b) Stale Connections (with slider)
years = st.sidebar.slider("Connections inactive for at least … years", min_value=1, max_value=10, value=3)
if st.sidebar.button("Show Stale Connections"):
    st.subheader(f"Connections Not Contacted in ≥ {years} Years")
    stale = stale_connections(years)
    df_stale = pd.DataFrame(stale)
    # you can format the date column nicely:
    df_stale["Connected On"] = pd.to_datetime(df_stale["Connected On"]).dt.date
    st.dataframe(df_stale)

# --- (Optional) Raw Data Viewer ---
st.sidebar.markdown("---")
if st.sidebar.checkbox("Show Raw Data"):
    df = pd.read_csv("data/Connections.csv", parse_dates=["Connected On"], dayfirst=True)
    st.subheader("Raw Exported Connections")
    st.dataframe(df)

# --- (Optional) Free-text Agent Console ---
st.sidebar.markdown("---")
st.sidebar.header("Ask your network (free-text)")
query = st.sidebar.text_input("Type a question…")
if st.sidebar.button("Run Query") and query:
    with st.spinner("🤖 Thinking…"):
        answer = agent.run(query)
    st.subheader("Agent Answer")
    st.write(answer)
    

st.sidebar.markdown("---")
st.sidebar.header("📅 Schedule a Meeting")

# Build a dict of all connections from your cleaned df
contacts = {
    f"{r['First Name']} {r['Last Name']}": r["URL"]
    for _, r in connections_df.iterrows()
    if r.get("First Name") and r.get("Last Name")
}

if contacts:
    person = st.sidebar.selectbox("Select Connection", list(contacts))
    meet_date = st.sidebar.date_input("Date", value=pd.Timestamp.today())
    meet_time = st.sidebar.time_input(
        "Time",
        value=datetime.now().replace(hour=9, minute=0).time()
    )

    if st.sidebar.button("Add Meeting"):
        dt = datetime.combine(meet_date, meet_time)
        new = {
            "Name": person,
            "URL": contacts[person],
            "Scheduled At": dt
        }

        # — Auto-create meetings.csv if it doesn't exist —
        if not os.path.exists("/Users/Navya/Documents/GitHub/AI-Agent/data"):
            os.makedirs("/Users/Navya/Documents/GitHub/AI-Agent/data")
        if os.path.exists("/Users/Navya/Documents/GitHub/AI-Agent/data/meetings.csv"):
            df_meet = pd.read_csv("/Users/Navya/Documents/GitHub/AI-Agent/data/meetings.csv", parse_dates=["Scheduled At"])
        else:
            df_meet = pd.DataFrame(columns=["Name","URL","Scheduled At"])

        # — Append & save —
        df_meet = pd.concat([df_meet, pd.DataFrame([new])], ignore_index=True)
        df_meet.to_csv("/Users/Navya/Documents/GitHub/AI-Agent/data/meetings.csv", index=False)

        st.sidebar.success(
            f"✅ Scheduled meeting with {person} on {dt:%b %d, %Y at %I:%M %p}"
        )
else:
    st.sidebar.write("No connections available.")

# —————— SIDEBAR: SHOW UPCOMING MEETINGS ——————
st.sidebar.markdown("---")
if st.sidebar.checkbox("Show Upcoming Meetings"):
    st.subheader("📋 Upcoming Meetings")
    if os.path.exists("/Users/Navya/Documents/GitHub/AI-Agent/data/meetings.csv"):
        df_up = pd.read_csv("/Users/Navya/Documents/GitHub/AI-Agent/data/meetings.csv", parse_dates=["Scheduled At"])
        df_up = df_up.sort_values("Scheduled At")
        # Format date for display
        df_up["Scheduled At"] = df_up["Scheduled At"].dt.strftime("%b %d, %Y %I:%M %p")
        st.dataframe(df_up)
    else:
        st.write("You haven’t scheduled any meetings yet.")
