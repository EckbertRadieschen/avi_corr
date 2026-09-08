import os
from dotenv import load_dotenv
from pathlib import Path

import geopandas as gpd
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine


# ============================================================
# KONFIGURATION
# ============================================================

TILE_GRID = Path("data/CONUS_C2_ARD_grid/CONUS_C2_ARD_grid.shp")

BUFFER_RADIUS_M = 1500

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

DB_CONFIG = {
    "host": MYSQL_HOST,
    "user": MYSQL_USER,
    "password": MYSQL_PASSWORD,
    "database": MYSQL_DATABASE
}

MYSQL_ENGINE = create_engine(f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}")

OUTPUT_TILES = "data/stop_nlcd_tiles_assignments.csv"


# ============================================================
# MYSQL - QUERY
# ============================================================

def load_stops():
    connection = mysql.connector.connect(**DB_CONFIG)

    query = """
        SELECT
            stop_id,
            route_id,
            latitude,
            longitude
        FROM analysis_stops;
    """

    stops = pd.read_sql(query, MYSQL_ENGINE)
    connection.close()

    return stops


# =======================================================
# GET RELEVANT TILES
# =======================================================

def create_stop_geodataframe(stops):
    return gpd.GeoDataFrame(
        stops,
        geometry=gpd.points_from_xy(
            stops["longitude"],
            stops["latitude"]
        ),
        crs="EPSG:4326",
    )


def assign_tiles(stops, tiles):
    stops = stops.to_crs(tiles.crs)

    stop_buffers = stops.copy()
    stop_buffers["geometry"] = stop_buffers.geometry.buffer(BUFFER_RADIUS_M)

    result = gpd.sjoin(
        stop_buffers,
        tiles[["h", "v", "geometry"]],
        how="left",
        predicate="intersects"
    )

    valid_tiles_filter = result["h"].notna()

    h_value = result.loc[valid_tiles_filter, "h"].astype(int).astype(str).str.zfill(2)
    v_value = result.loc[valid_tiles_filter, "v"].astype(int).astype(str).str.zfill(2)

    result.loc[valid_tiles_filter, "tile_id"] = "H" + h_value + "V" + v_value

    return result


# ==========================================================================
# EVALUATE RELEVANT TILES
# ==========================================================================

def analyse_tiles(result):
    stop_count = result["stop_id"].nunique()
    print(f"\nAnzahl Stopps insgesamt: {stop_count:,}")

    missing = result["h"].isna().sum()
    print(f"Stops ohne zugeordnetes Tile: {missing:,}")

    required_tiles = (
        result[["tile_id"]]
        .dropna()
        .drop_duplicates()
        .sort_values("tile_id")
        .reset_index(drop=True)
    )

    print(f"\nBenötigte Tiles für {BUFFER_RADIUS_M:,}-m-Buffer: {len(required_tiles):,}")

    tile_assignments = result[["stop_id", "latitude", "longitude", "h", "v", "tile_id"]]
    tile_assignments.to_csv(OUTPUT_TILES, index=False)

    print("\nDateien gespeichert:")
    print(OUTPUT_TILES)


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("Zuordnung Stops -> NLCD Tiles")
    print("=" * 60)

    stops = load_stops()
    stops = create_stop_geodataframe(stops)
    tiles = gpd.read_file(TILE_GRID)
    result = assign_tiles(stops, tiles)
    analyse_tiles(result)
    


if __name__ == "__main__":
    main()

