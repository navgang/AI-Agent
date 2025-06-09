import os
import re
import csv
import pandas as pd

# 0) Path to your CSV
CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "Connections.csv")

# 1) Read entire file, sniff delimiter, fall back to comma
with open(CSV_PATH, newline="", encoding="utf-8") as f:
    sample = f.read(1024)
    f.seek(0)
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=[",", ";", "\t"])
        delim = dialect.delimiter
    except csv.Error:
        delim = ","
    reader = csv.reader(f, delimiter=delim)
    rows = [row for row in reader if any(cell.strip() for cell in row)]  # drop blank rows

# 2) Separate header and data
header = rows[0]
num_cols = len(header)
data_rows = [row for row in rows[1:] if len(row) == num_cols]

# 3) Build DataFrame
df = pd.DataFrame(data_rows, columns=header)

# 4) Clean up whitespace
df = df.applymap(lambda v: v.strip() if isinstance(v, str) else v)

# 5) Parse your date column
if "Connected On" in df.columns:
    df["Connected On"] = pd.to_datetime(
        df["Connected On"], dayfirst=True, errors="coerce"
    )
else:
    raise ValueError("Expected a 'Connected On' column in Connections.csv")

# — now your tools can operate on `df` —
def top_companies(n=5):
    # 1) Coerce n into an integer
    try:
        n_int = int(n)
    except:
        m = re.search(r"\d+", str(n))
        n_int = int(m.group()) if m else 5

    series = (
        df["Company"]
          .fillna("")         # NaN→""
          .astype(str)
          .str.strip()
    )
    # drop empty
    series = series[series != ""]

    counts = series.value_counts().head(n_int)
    return counts.to_dict()

def stale_connections(years=3):
    """
    Returns connections not touched in X years.
    Coerces inputs like "years=3" into the integer 3.
    """
    # 1) Coerce years → int
    try:
        years_int = int(years)
    except Exception:
        m = re.search(r"\d+", str(years))
        years_int = int(m.group()) if m else 3

    # 2) Compute cutoff
    cutoff = pd.Timestamp.today() - pd.DateOffset(years=years_int)

    # 3) Filter your DataFrame (assuming your df is called `df`)
    stale = df[df["Company"].notna() & (df["Connected On"] < cutoff)]
    return stale[[
        "First Name","Last Name","URL","Position","Company","Connected On"
    ]].to_dict(orient="records")

from openai import OpenAI
oai = OpenAI()
connections_df = df