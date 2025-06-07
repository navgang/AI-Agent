import pandas as pd
from linkedin_api import Linkedin
from openai import OpenAI

# 1) Load connections CSV
df = pd.read_csv("data/Connections.csv", parse_dates=["Connected On"])

# 2) Analytics
def top_companies(n=5):
    return df["Company"].value_counts().head(n).to_dict()

def stale_connections(years=3):
    cutoff = pd.Timestamp.today() - pd.DateOffset(years=years)
    stale = df[df["Connected On"] < cutoff]
    return stale[["First Name","Last Name","LinkedIn URL"]].to_dict(orient="records")

# 3) Message tool
oai = OpenAI()
def craft_message(first_name, company, role):
    prompt = (
      f"Write a friendly LinkedIn message to {first_name}, a {role} at {company}, "
      "mentioning our shared AI product interest and asking to reconnect."
    )
    resp = oai.chat.completions.create(
      model="gpt-4o-mini",
      messages=[{"role":"user","content":prompt}],
    )
    return resp.choices[0].message.content