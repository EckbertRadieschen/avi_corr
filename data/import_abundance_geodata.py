import os
from pathlib import Path
import requests
import geopandas as gpd
import mysql.connector
from dotenv import load_dotenv

# ========================================================
load_dotenv()
ACCESS_KEY = os.getenv("EBIRD_ACCESS_KEY_ID")
LIST_URL = os.getenv("EBIRD_LIST_URL")
DOWNLOAD_URL = os.getenv("EBIRD_DOWNLOAD_URL")
OBJ_KEY_PREFIX = r"2023/"
OBJ_KEY_MIDDLE = r"/ranges/"
OBJ_KEY_SUFFIX = r"_range_smooth_9km_2023.gpkg"
TEMP_DIR = Path("ebird_temp")
TEMP_DIR.mkdir(exist_ok=True)

# =========================================================
db = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE", "bbs_analysis")
)
cursor = db.cursor()

# =========================================================
cursor.execute("""
    SELECT ebird_species_code
    FROM analysis_species_list
    WHERE ebird_species_code IS NOT NULL
    ORDER BY ebird_species_code
""")
species_codes = [row[0] for row in cursor.fetchall()]

# =========================================================
insert_sql = """
    INSERT INTO ebird_breeding_ranges (
        species_code,
        min_latitude,
        max_latitude,
        breeding_start,
        breeding_end
    )
    VALUES (%s, %s, %s, %s, %s)
"""

# =========================================================
for number, species_code in enumerate(species_codes, start=1):
    print(f"[{number}/{len(species_codes)}] - {species_code}")
    temp_file = TEMP_DIR / f"{species_code}_range.gpkg"
    try:
        object = rf"{OBJ_KEY_PREFIX}{species_code}{OBJ_KEY_MIDDLE}{species_code}{OBJ_KEY_SUFFIX}"
        response = requests.get(
            DOWNLOAD_URL,
            params={
                "key": ACCESS_KEY,
                "objKey": object
            },
            stream=True,
            timeout=300
        )
        response.raise_for_status()
        with open(temp_file, "wb") as file:
            file.write(response.content)
        
        gdf = gpd.read_file(temp_file, layer="range")
        season_filter = gdf["season"] == "breeding"
        breeding = gdf[season_filter]
        if breeding.empty:
            continue
        bounds = breeding.total_bounds
        min_latitude = bounds[1]
        max_latitude = bounds[3]
        
        breeding_start = breeding["start_date"].iloc[0]
        breeding_end = breeding["end_date"].iloc[0]
        cursor.execute(
            insert_sql,
            (
                species_code,
                min_latitude,
                max_latitude,
                breeding_start,
                breeding_end
            )
        )
        db.commit()
    except Exception as error:
        print(f"Error in {species_code}:")
        print(error)
    finally:
        if temp_file.exists():
            temp_file.unlink()
            
cursor.close()
db.close()

