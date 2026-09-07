import os
from dotenv import load_dotenv

import pandas as pd
import mysql.connector


# -------------------------------------------------- 
# Umgebungsvariablen laden 
# -------------------------------------------------- 

load_dotenv()

# --------------------------------------------------
# Datenbankverbindung
# --------------------------------------------------

connection = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    port=os.getenv("MYSQL_PORT"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE")
)


# --------------------------------------------------
# Relevante Route-Stop-Jahr-Kombinationen laden
# --------------------------------------------------

query_stops_years = """
SELECT
    s.route_id,
    s.stop_number,
    s.latitude,
    s.longitude,
    s.position_accuracy,
    ry.year
FROM analysis_stops AS s
JOIN analysis_route_years AS ry
    ON ry.route_id = s.route_id
ORDER BY
    s.route_id,
    s.stop_number,
    ry.year;
"""

df_stops_years = pd.read_sql(
    query_stops_years,
    connection
)


# --------------------------------------------------
# Verbindung schließen
# --------------------------------------------------

connection.close()


# --------------------------------------------------
# Kontrolle
# --------------------------------------------------

print(
    df_stops_years.groupby("route_id")["year"]
    .nunique()
    .describe()
)


