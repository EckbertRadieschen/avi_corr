import os
from dotenv import load_dotenv
from pathlib import Path

import geopandas as gpd
import pandas as pd
import mysql.connector


# ============================================================
# KONFIGURATION
# ============================================================

TILE_GRID = Path("data/CONUS_C2_ARD_grid.shp")

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

OUTPUT_TILES = "required_nlcd_tiles.csv"
OUTPUT_TILE_COUNTS = "required_nlcd_tiles_with_counts.csv"


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

    stops = pd.read_sql(query, connection)
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

    valid_tiles = result["h"].notna()

    h_value = result.loc[valid_tiles, "h"].astype(int).astype(str).str.zfill(2)
    v_value = result.loc[valid_tiles, "v"].astype(int).astype(str).str.zfill(2)

    result.loc[valid_tiles, "tile_id"] = "H" + h_value + "V" + v_value

    return result


# ==========================================================================
# EVALUATE RELEVANT TILES
# ==========================================================================

def analyse_tiles(result):
    stop_count = result["stop_id"].nunique()
    print(f"\nUrsprüngliche Stopps: {stop_count:,}")

    missing = result["h"].isna().sum()
    print(f"Zeilen ohne Tile-Zuordnung: {missing:,}")

    required_tiles = (
        result[["tile_id"]]
        .dropna()
        .drop_duplicates()
        .sort_values("tile_id")
        .reset_index(drop=True)
    )

    print(f"\nBenötigte Tiles für {BUFFER_RADIUS_M:,}-m-Buffer: {len(required_tiles):,}")

    return required_tiles


# ============================================================
# MAIN
# ============================================================

def main():
    stops = load_stops()
    stops = create_stop_geodataframe(stops)
    tiles = gpd.read_file(TILE_GRID)
    result = assign_tiles(stops, tiles)
    required_tiles = analyse_tiles(result)

    required_tiles.to_csv(OUTPUT_TILES, index=False)

    print("\nBenötigte Tiles:")
    print(required_tiles.to_string(index=False))

    print("\nDateien gespeichert:")
    print(OUTPUT_TILES)
    print(OUTPUT_TILE_COUNTS)


if __name__ == "__main__":
    main()

