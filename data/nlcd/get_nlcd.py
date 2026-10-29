import os
import re
from pathlib import Path

import boto3
import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio

from dotenv import load_dotenv
from rasterio.features import geometry_mask, geometry_window
from rasterio.errors import WindowError
from shapely.geometry import mapping
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
NLCD_DIR = DATA_DIR / "nlcd"

TILE_GRID = NLCD_DIR / "CONUS_C2_ARD_grid/CONUS_C2_ARD_grid.shp"
TILE_MAPPING_FILE = NLCD_DIR / "stop_nlcd_tiles_assignments.csv"

BUFFER_RADIUS_M = 1500
START_YEAR = 1985
END_YEAR = 2025
YEARS = range(START_YEAR, END_YEAR + 1)


LANDCOVER_GROUPS = {
    "water": [11],
    "developed": [21, 22, 23, 24],
    "barren": [31],
    "forest": [41, 42, 43],
    "shrubland": [52],
    "grassland": [71],
    "pasture": [81],
    "cropland": [82],
    "wetland": [90, 95]
}

# --------------------------------------------------
# AWS
# --------------------------------------------------

AWS_REGION = "us-west-2"
AWS_BUCKET = "usgs-landcover"
AWS_BASE_PREFIX = ("annual-nlcd/c1/v2/cu/tile")

s3 = boto3.client("s3", region_name=AWS_REGION)
NLCD_PRODUCT = "LndCov"

# --------------------------------------------------
# MySQL
# --------------------------------------------------

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

ENGINE = create_engine(DATABASE_URL, pool_pre_ping=True)


def create_result_dictionary(stop_tile_assignments, years):
   
    landcover_indexes = []
    for index_list in LANDCOVER_GROUPS.values():
        landcover_indexes.append(index_list)

    result_dictionary = {}

    for stop_id in stop_tile_assignments["stop_id"].unique():
        result_dictionary[stop_id] = {}

        for year in years:
            result_dictionary[stop_id][year] = {}

            for index in landcover_indexes:
                result_dictionary[stop_id][year][index] = 0

    return result_dictionary


# ============================================================
# Stop - Tile - Zuordnung 
# ============================================================

def get_stop_tile_assignments():
    return pd.read_csv(TILE_MAPPING_FILE)


def get_tile_ids(mapping_df): 
    return sorted(mapping_df["tile_id"].unique())


def get_tile_stops(mapping_df, tile_id):  
    filter = mapping_df["tile_id"] == tile_id

    return mapping_df.loc[filter, "stop_id"].drop_duplicates().tolist()


def create_stop_buffers(stop_df, target_crs):
    
    stops_gdf = gpd.GeoDataFrame(
        stop_df.copy(), 
        geometry=gpd.points_from_xy(
            stop_df["longitude"], 
            stop_df["latitude"]), 
            crs="EPSG:4326"
        ) 
    
    stops_gdf = stops_gdf.to_crs(target_crs) 
    stops_gdf["buffer"] = stops_gdf.geometry.buffer(BUFFER_RADIUS_M) 
    
    return dict(
        zip(stops_gdf["stop_id"], stops_gdf["buffer"])
    )


# ===================================================================================================
# Relevante TIFF-Dateien ansteuern
# ===================================================================================================

def list_landcover_files(s3, tile_id): 
    tile_prefix = f"{AWS_BASE_PREFIX}/{tile_id.lower()}/"
    paginator = s3.get_paginator("list_objects_v2") 
    files = [] 
    
    for page in paginator.paginate(Bucket=AWS_BUCKET, Prefix=tile_prefix, RequestPayer="requester"): 
        for obj in page.get("Contents", []): 
            key = obj["Key"] 
            filename = Path(key).name 

            if f"_{NLCD_PRODUCT}_" in filename and filename.lower().endswith(".tif"): 
                files.append(
                    {
                        "key": key, 
                        "size": obj["Size"]
                    }
                )

    return files


# ===================================================================================================
# TIFF-Dateien das zugehörige Jahr zuordnen
# ===================================================================================================

def organize_files_by_year(files): 
    files_by_year = {} 
    
    for file_info in files: 
        key = file_info["key"]
        match = re.search(r"_(\d{4})_CU_C1V2\.tif$", key, re.IGNORECASE)
        if not match: 
            raise ValueError(f"Jahr konnte nicht aus S3-Key gelesen werden:\n{key}")
        else:
            year = int(match.group(1))
        
        if not START_YEAR <= year <= END_YEAR: 
            continue 
        if year in files_by_year:
            raise ValueError(f"Mehrere Dateien für {year} gefunden") 
        
        files_by_year[year] = file_info 

    return files_by_year


# ===================================================================================================
# Eine Datei über AWS herunterladen
# ===================================================================================================

def download_nlcd_file(s3, key, destination):
    print(f"Download von: s3://{AWS_BUCKET}/{key}") 
    destination.parent.mkdir(parents=True, exist_ok=True) 
    temporary_file = destination.with_suffix(destination.suffix + ".part") 
    
    try: 
        response = s3.get_object(Bucket=AWS_BUCKET, Key=key, RequestPayer="requester") 

        with open(temporary_file, "wb") as file: 
            while chunk := response["Body"].read(8 * 1024 * 1024): 
                file.write(chunk) 

        temporary_file.replace(destination) 

    except Exception: 
        if temporary_file.exists(): 
            temporary_file.unlink() 

        raise


# =============================================================================================================
# RASTER-VERARBEITUNG 
# =============================================================================================================

def read_buffer_pixels(dataset, geometry): 
    try:
        geometry_list = [mapping(geometry)]
        window = geometry_window(dataset, geometry_list) # Reduktion des Rasters auf einen kleinstmöglichen Bereich
    
    except WindowError: 
        return np.array([]) 
    
    array = dataset.read(1, window=window) 
    transform = dataset.window_transform(window) 
    mask = geometry_mask(geometry_list, out_shape=array.shape, transform=transform, invert=True, all_touched=False) 
    
    return array[mask]


# =============================================================================================================
# Tile-Verarbeitungsfunktion für den Tile-Loop 
# =============================================================================================================

def process_tile(s3, tile_id, tile_crs, stop_df, landcover_counts): 
    print(f"\nTile {tile_id}") 
    print("-" * 40) 

    stop_ids = get_tile_stops(stop_df, tile_id) 
    tile_stop_df = stop_df[stop_df["stop_id"].isin(stop_ids)]
    stop_buffers = create_stop_buffers(tile_stop_df, tile_crs)

    files = list_landcover_files(s3, tile_id) 
    files_by_year = organize_files_by_year(files) 

    print(f"{len(stop_ids):,} Stops | {len(files_by_year)} Jahre")  

    download_count = 0
    download_total = END_YEAR - START_YEAR + 1
    for year in range(START_YEAR, END_YEAR + 1): 
        year_results = {}

        download_count += 1
        if year not in files_by_year:
            print("Jahr nicht verfügbar")
            continue
        
        file_info = files_by_year[year]
        local_path = NLCD_DIR / Path(file_info["key"]).name 

        print(f"Downloade Datei {download_count}/{download_total}")
        download_nlcd_file(s3, file_info["key"], local_path)  
        
        try: 
            with rasterio.open(local_path) as dataset: 
                for stop_id in stop_ids:
                    values = read_buffer_pixels(dataset, stop_buffers[stop_id])

                    if values.size == 0: 
                        class_counts = {} 

                    else:
                        classes, counts = np.unique(values, return_counts=True) 
                        class_counts = dict(zip(classes, counts))

                    year_results[stop_id] = class_counts
                    target = landcover_counts[stop_id][year]
                    
                    for nlcd_class, count in class_counts.items(): 
                        if nlcd_class in target:
                            target[nlcd_class] += count

        finally: 
            if local_path.exists(): 
                local_path.unlink()
            
    return landcover_counts


# ===================================================================================================
# Finalen DataFrame für den Datenexport erzeugen
# ===================================================================================================

def create_result_dataframe(landcover_counts): 
    rows = [] 
    
    for stop_id, year_dicts in landcover_counts.items(): 
        for year, class_counts in year_dicts.items():
            valid_pixels = sum(
                count 
                for nlcd_class, count in class_counts.items() 
                if nlcd_class != 0 
            ) 
        
            fractions = {group: 0.0 for group in LANDCOVER_GROUPS} 
            
            if valid_pixels != 0: 
                for group, classes in LANDCOVER_GROUPS.items(): 
                    group_pixels = sum(
                        class_counts.get(nlcd_class, 0) 
                        for nlcd_class in classes 
                    ) 
                    
                    fractions[group] = round(group_pixels / valid_pixels, 4) 

            rows.append(
                {
                    "stop_id": stop_id,
                    "year": year,
                    **fractions
                }
            )
    
    return pd.DataFrame(rows)


# ===================================================================================================
# Daten in Datenbank exportieren
# ===================================================================================================

def save_all(landcover_dict): 

    result_df = create_result_dataframe(landcover_dict) 
    if result_df.empty: 
        return 
    
    result_df.to_sql(
        "nlcd_year_data", 
        ENGINE, 
        if_exists="append", 
        index=False, 
        chunksize=5000, 
        method="multi"
    ) 


# ===================================================================================================
# Hauptfunktion
# ===================================================================================================

def main(): 
    print("NLCD-Verarbeitung wird gestartet") 

    mapping_df = get_stop_tile_assignments() 

    tile_ids = get_tile_ids(mapping_df) 
    tile_grid = gpd.read_file(TILE_GRID) 
    tile_crs = tile_grid.crs 

    landcover_dict = create_result_dictionary(mapping_df, YEARS)
    
    for number, tile_id in enumerate(tile_ids, start=1): 
        print() 
        print(f"[{number}/{len(tile_ids)}]") 
        
        process_tile(s3=s3, tile_id=tile_id, tile_crs=tile_crs, stop_df=mapping_df, landcover_counts=landcover_dict) 

    save_all(landcover_dict)
         
    print("\nNLCD-Verarbeitung abgeschlossen")


if __name__ == "__main__":
    main()

    