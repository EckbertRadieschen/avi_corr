import os
from dotenv import load_dotenv

import pandas as pd
import json
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

ROUTE_CONFIG_PATH = "src/config/route_config.json"
SPECIES_CONFIG_PATH = "src/config/species_config.json"

SPECIES_ZIP_PATH = "data/processed/species_csv_files.zip"

route_query = """
SELECT 
    r.state_num * 1000 + CAST(r.route AS UNSIGNED) AS route_id,
    st.state_name AS state,
    CASE 
        WHEN st.country_num = 124 THEN "Canada"
        WHEN st.country_num = 840 THEN "USA"
        ELSE "Missing"
    END AS country,
    r.latitude,
    r.longitude
FROM routes AS r
JOIN bbs_states AS st
    ON r.state_num = st.state_num
ORDER BY route_id;
"""

full_observation_query = """
    SELECT
        state_num * 1000 + CAST(route AS UNSIGNED) AS route_id,
        aou AS species_id,
        `year`,
        species_total
    FROM bird_observations
    WHERE rpid = 101
    ORDER BY route_id, `year`, species_id;
"""

# ======================================================================

def setup_route_config():
    route_df = pd.read_sql(route_query, ENGINE)

    route_config = route_df.set_index("route_id").to_dict(orient="index")

    for config in route_config.values():
        config["high_count_ratios"] = {}

    with open(ROUTE_CONFIG_PATH, "w") as file:
        json.dump(route_config, file, ensure_ascii=False, indent=4)


def add_high_count_ration_to_config():
    with open(ROUTE_CONFIG_PATH, "r") as file:
        route_config = json.load(file)

    with open(SPECIES_CONFIG_PATH, "r") as file:
        species_config = json.load(file)

    print("Import observation data from database...")

    observation_df = pd.read_sql(full_observation_query, ENGINE)

    observation_df["route_id"] = observation_df["route_id"].astype(str)

    for species_id, species_dict in species_config.items():
        print(f"Working on species {species_id}")

        high_count_cap = species_dict["meta_data"]["high_count_cap"]

        species_filter = observation_df["species_id"] == species_id
        species_df = observation_df[species_filter].copy()

        route_high_count_series = (
            species_df
            .groupby("route_id")["species_total"]
            .apply(lambda x: (x >= high_count_cap).sum() / len(x))
        )

        for route_id, route_dict in route_config.items():
            if not route_id in list(route_high_count_series.index):
                continue
            
            route_dict["high_count_ratios"][species_id] = route_high_count_series.loc[route_id]

        with open(ROUTE_CONFIG_PATH, "w") as file:
            json.dump(route_config, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    # setup_route_config()
    add_high_count_ration_to_config()