import os
from dotenv import load_dotenv

import pandas as pd
from sqlalchemy.engine import URL
from sqlalchemy import create_engine


load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")


DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=MYSQL_USER,
    password=MYSQL_PASSWORD,
    host=MYSQL_HOST,
    database=MYSQL_DATABASE
)

ENGINE = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# =====================================================

query = """
SELECT
    o.*,
    n.water,
    n.developed,
    n.barren,
    n.forest,
    n.shrubland,
    n.grassland,
    n.pasture,
    n.cropland,
    n.wetland
FROM analysis_relevant_observations AS o
JOIN nlcd_route_analysis AS n
    ON o.route_id = n.route_id AND o.`year` = n.`year`;
"""

df = pd.read_sql(query, ENGINE)

file_url = rf"data/processed/full_bbs_landcover.csv"
    
df.to_csv(file_url, index=False)