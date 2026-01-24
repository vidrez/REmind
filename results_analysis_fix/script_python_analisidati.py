# Python 3.10.x
# pip install mysql-connector-python pandas matplotlib seaborn

import mysql.connector
import pandas as pd
import os

# =========================
# CONFIG
# =========================

OUTPUT_DIR = "telemetry_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

conn = mysql.connector.connect(
    host="",
    port=,
    user="root",
    password="",   # cambia
    database="remind_db"
)

# =========================
# LOAD EVENTS WITH DELTA TIME
# =========================

query_events = """
WITH ordered AS (
  SELECT
    id,
    user_id,
    challenge,
    fcn_name,
    CAST(JSON_EXTRACT(event, '$.timestamp') AS UNSIGNED) AS ts,
    JSON_EXTRACT(event, '$.event') AS ev_type,
    JSON_EXTRACT(event, '$.element') AS element,
    LEAD(CAST(JSON_EXTRACT(event, '$.timestamp') AS UNSIGNED))
      OVER (PARTITION BY user_id, challenge ORDER BY CAST(JSON_EXTRACT(event, '$.timestamp') AS UNSIGNED)) AS next_ts
  FROM events
)
SELECT *,
       (next_ts - ts) AS delta_ms
FROM ordered
WHERE next_ts IS NOT NULL;
"""

df = pd.read_sql(query_events, conn)

# =========================
# CLEANING (optional but recommended)
# =========================

df = df[(df["delta_ms"] > 50) & (df["delta_ms"] < 10000)]

# =========================
# 1) TIME PER CHALLENGE
# =========================

time_per_challenge = (
    df.groupby(["user_id", "challenge"])["delta_ms"]
    .sum()
    .reset_index()
)

time_per_challenge["total_time_sec"] = time_per_challenge["delta_ms"] / 1000
time_per_challenge.drop(columns=["delta_ms"], inplace=True)

time_per_challenge.to_csv(f"{OUTPUT_DIR}/time_per_challenge.csv", index=False)

# =========================
# 2) TIME PER FUNCTION
# =========================

time_per_function = (
    df.groupby(["user_id", "challenge", "fcn_name"])["delta_ms"]
    .sum()
    .reset_index()
)

time_per_function["time_sec"] = time_per_function["delta_ms"] / 1000
time_per_function.drop(columns=["delta_ms"], inplace=True)

time_per_function.to_csv(f"{OUTPUT_DIR}/time_per_function.csv", index=False)

# =========================
# 3) BASIC BLOCKS PER CHALLENGE
# =========================

bb_df = df[df["ev_type"] == '"mouseover"']

bb_per_challenge = (
    bb_df.groupby(["user_id", "challenge"])["element"]
    .nunique()
    .reset_index()
    .rename(columns={"element": "unique_bb"})
)

bb_per_challenge.to_csv(f"{OUTPUT_DIR}/bb_per_challenge.csv", index=False)


# Python 3.10.x
# pip install mysql-connector-python pandas matplotlib seaborn

import mysql.connector
import pandas as pd
import os

# =========================
# CONFIG
# =========================

OUTPUT_DIR = "telemetry_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

conn = mysql.connector.connect(
    host="127.0.0.1",
    port=3307,
    user="root",
    password="rootpass",   # cambia
    database="remind_db"
)

# =========================
# LOAD EVENTS WITH DELTA TIME
# =========================

query_events = """
WITH ordered AS (
  SELECT
    id,
    user_id,
    challenge,
    fcn_name,
    CAST(JSON_EXTRACT(event, '$.timestamp') AS UNSIGNED) AS ts,
    JSON_EXTRACT(event, '$.event') AS ev_type,
    JSON_EXTRACT(event, '$.element') AS element,
    LEAD(CAST(JSON_EXTRACT(event, '$.timestamp') AS UNSIGNED))
      OVER (PARTITION BY user_id, challenge ORDER BY CAST(JSON_EXTRACT(event, '$.timestamp') AS UNSIGNED)) AS next_ts
  FROM events
)
SELECT *,
       (next_ts - ts) AS delta_ms
FROM ordered
WHERE next_ts IS NOT NULL;
"""

df = pd.read_sql(query_events, conn)

# =========================
# CLEANING (optional but recommended)
# =========================

df = df[(df["delta_ms"] > 50) & (df["delta_ms"] < 10000)]

# =========================
# 1) TIME PER CHALLENGE
# =========================

time_per_challenge = (
    df.groupby(["user_id", "challenge"])["delta_ms"]
    .sum()
    .reset_index()
)

time_per_challenge["total_time_sec"] = time_per_challenge["delta_ms"] / 1000
time_per_challenge.drop(columns=["delta_ms"], inplace=True)

time_per_challenge.to_csv(f"{OUTPUT_DIR}/time_per_challenge.csv", index=False)

# =========================
# 2) TIME PER FUNCTION
# =========================

time_per_function = (
    df.groupby(["user_id", "challenge", "fcn_name"])["delta_ms"]
    .sum()
    .reset_index()
)

time_per_function["time_sec"] = time_per_function["delta_ms"] / 1000
time_per_function.drop(columns=["delta_ms"], inplace=True)

time_per_function.to_csv(f"{OUTPUT_DIR}/time_per_function.csv", index=False)

# =========================
# 3) BASIC BLOCKS PER CHALLENGE
# =========================

bb_df = df[df["ev_type"] == '"mouseover"']

bb_per_challenge = (
    bb_df.groupby(["user_id", "challenge"])["element"]
    .nunique()
    .reset_index()
    .rename(columns={"element": "unique_bb"})
)

bb_per_challenge.to_csv(f"{OUTPUT_DIR}/bb_per_challenge.csv", index=False)



# ============================================================
# 5) FIGURE 5 — TRACE TEMPORALE BASIC BLOCK (CSV UNICO)
# ============================================================

query_fig5 = """
SELECT
    user_id,
    challenge,
    CAST(JSON_EXTRACT(event, '$.timestamp') AS UNSIGNED) AS timestamp,
    JSON_UNQUOTE(JSON_EXTRACT(event, '$.event')) AS ev_type,
    JSON_UNQUOTE(JSON_EXTRACT(event, '$.element')) AS basic_block
FROM events
WHERE JSON_UNQUOTE(JSON_EXTRACT(event, '$.event')) = 'mouseover'
  AND JSON_EXTRACT(event, '$.element') IS NOT NULL
  AND JSON_UNQUOTE(JSON_EXTRACT(event, '$.element')) <> ''
ORDER BY user_id, challenge, timestamp;
"""

# Evita possibili incompatibilità di pandas.read_sql con mysql.connector:
cur = conn.cursor()
cur.execute(query_fig5)
rows = cur.fetchall()
cols = [d[0] for d in cur.description]
df_fig5 = pd.DataFrame(rows, columns=cols)

# tieni solo le colonne che vuoi nel CSV finale
df_fig5 = df_fig5[["user_id", "challenge", "timestamp", "basic_block"]]

def hex_to_dec(x):
    try:
        return int(x, 16)  # converte "0x4005f0" -> 4195824
    except:
        return None

df_fig5["basic_block_dec"] = df_fig5["basic_block"].apply(hex_to_dec)
df_fig5 = df_fig5[["user_id", "challenge", "timestamp", "basic_block_dec"]]

df_fig5["t0"] = df_fig5.groupby(["user_id", "challenge"])["timestamp"].transform("min")
df_fig5["rel_time_ms"] = df_fig5["timestamp"] - df_fig5["t0"]
df_fig5["rel_time_sec"] = df_fig5["rel_time_ms"] / 1000.0
df_fig5 = df_fig5 = df_fig5[["user_id", "challenge", "timestamp", "rel_time_sec"]]


fig5_path = os.path.join(OUTPUT_DIR, "figure5_trace.csv")
df_fig5.to_csv(fig5_path, index=False)

print("Result in ", OUTPUT_DIR)
