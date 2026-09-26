import os
from dotenv import load_dotenv

from zipfile import ZipFile
import pandas as pd
import numpy as np
from sqlalchemy.engine import URL
from sqlalchemy import create_engine

from scipy.stats import pearsonr, spearmanr
import statsmodels.api as sm


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

ZIP_PATH = "data/processed/species_csv_files.zip"
DISTRIBUTION_FILES_DIR = "data/processed/distribution_check_files"

INDICATORS = {
    "climate": {
        "temperature": [
            "mean_year", "mean_spring", "mean_summer", "mean_fall", "mean_winter",
            "min_year", "min_spring", "min_summer", "min_fall", "min_winter",
            "max_year", "max_spring", "max_summer", "max_fall", "max_winter",
            "std_year", "std_spring", "std_summer", "std_fall", "std_winter"
        ],
        "precipitation": ["sum_year", "sum_spring", "sum_summer", "sum_fall", "sum_winter", "max_month"],
        "snowfall": ["sum_year", "sum_spring", "sum_summer", "sum_fall", "sum_winter", "max_month"],
        "wind_magnitude": ["mean_year", "mean_spring", "mean_summer", "mean_fall", "mean_winter", "max_year"],
        "relative_humidity": [
            "mean_year", "mean_spring", "mean_summer", "mean_fall", "mean_winter",
            "min_year", "min_spring", "min_summer", "min_fall", "min_winter",
            "max_year", "max_spring", "max_summer", "max_fall", "max_winter",
            "std_year", "std_spring", "std_summer", "std_fall", "std_winter"
        ],
        "soil_moisture": [
            "mean_year", "mean_spring", "mean_summer", "mean_fall", "mean_winter",
            "min_year", "min_spring", "min_summer", "min_fall", "min_winter",
            "max_year", "max_spring", "max_summer", "max_fall", "max_winter",
            "std_year", "std_spring", "std_summer", "std_fall", "std_winter"
        ],
        "solar_flux_density": ["mean_year", "mean_spring", "mean_summer", "mean_fall", "mean_winter"],
        "vegetation_coeff": ["mean_year", "mean_spring", "mean_summer", "mean_fall", "mean_winter"]
    },
    "land_cover": {
        "water": [None],
        "developed": [None],
        "barren": [None],
        "forest": [None],
        "shrubland": [None],
        "grassland": [None],
        "pasture": [None],
        "cropland": [None],
        "wetland": [None]
    }
}

INDICATOR_LIST = [
    "temperature_mean_year", "temperature_mean_spring",
    "temperature_mean_summer", "temperature_mean_fall", "temperature_mean_winter",
    "temperature_min_year", "temperature_max_year", "temperature_min_spring",
    "temperature_max_spring", "temperature_min_summer", "temperature_max_summer",
    "temperature_min_fall", "temperature_max_fall", "temperature_min_winter",
    "temperature_max_winter", "temperature_std_year", "temperature_std_spring",
    "temperature_std_summer", "temperature_std_fall", "temperature_std_winter",

    "precipitation_sum_year", "precipitation_sum_spring", "precipitation_sum_summer",
    "precipitation_sum_fall", "precipitation_sum_winter", "precipitation_max_month",

    "snowfall_sum_year", "snowfall_sum_spring", "snowfall_sum_summer",
    "snowfall_sum_fall", "snowfall_sum_winter", "snowfall_max_month",

    "wind_magnitude_mean_year", "wind_magnitude_mean_spring", "wind_magnitude_mean_summer",
    "wind_magnitude_mean_fall", "wind_magnitude_mean_winter", "wind_magnitude_max_year",

    "relative_humidity_mean_year", "relative_humidity_mean_spring",
    "relative_humidity_mean_summer", "relative_humidity_mean_fall", "relative_humidity_mean_winter",
    "relative_humidity_min_year", "relative_humidity_max_year", "relative_humidity_min_spring",
    "relative_humidity_max_spring", "relative_humidity_min_summer", "relative_humidity_max_summer",
    "relative_humidity_min_fall", "relative_humidity_max_fall", "relative_humidity_min_winter",
    "relative_humidity_max_winter", "relative_humidity_std_year", "relative_humidity_std_spring",
    "relative_humidity_std_summer", "relative_humidity_std_fall", "relative_humidity_std_winter",

    "soil_moisture_mean_year", "soil_moisture_mean_spring",
    "soil_moisture_mean_summer", "soil_moisture_mean_fall", "soil_moisture_mean_winter", 
    "soil_moisture_min_year", "soil_moisture_max_year", "soil_moisture_min_spring",
    "soil_moisture_max_spring", "soil_moisture_min_summer", "soil_moisture_max_summer",
    "soil_moisture_min_fall", "soil_moisture_max_fall", "soil_moisture_min_winter",
    "soil_moisture_max_winter", "soil_moisture_std_year", "soil_moisture_std_spring",
    "soil_moisture_std_summer", "soil_moisture_std_fall", "soil_moisture_std_winter",

    "solar_flux_density_mean_year", "solar_flux_density_mean_spring", "solar_flux_density_mean_summer",
    "solar_flux_density_mean_fall", "solar_flux_density_mean_winter",

    "vegetation_coeff_mean_year", "vegetation_coeff_mean_spring", "vegetation_coeff_mean_summer",
    "vegetation_coeff_mean_fall", "vegetation_coeff_mean_winter",

    "water", "developed", "barren", "forest", "shrubland",
    "grassland", "pasture", "cropland", "wetland"
]

# =====================================================

def get_species_list ():
    species_query = """
        SELECT DISTINCT
            species_id,
            scientific_name,
            common_name,
            `order`,
            family,
            genus
        FROM analysis_species_list
        ORDER BY species_id;
    """
    
    species_df = pd.read_sql(species_query, ENGINE)

    pre_list = species_df["species_id"].tolist()

    species_list = []

    with ZipFile(ZIP_PATH, "r") as zip:
        for species_id in pre_list:
            species_id_str = str(species_id).zfill(5)
            filename = f"{species_id_str}.csv"

            try:
                with zip.open(filename) as _:
                    species_list.append(species_id_str)

            except:
                continue

    return species_list

def get_species_analysis_frame (species_id):
    filename = f"{species_id}.csv"

    try:
        with ZipFile(ZIP_PATH, "r") as zip:
            with zip.open(filename) as file:
                return pd.read_csv(file, encoding="utf-8")
    except:
        raise FileNotFoundError


def reduce_analysis_frame (df: pd.DataFrame):

    indicator_df = df.copy()
    sufficient_routes = indicator_df.loc[0, "sufficient_routes"] == 1

    analysis_index_list = []
    
    for route_id in list(indicator_df["route_id"].unique()):
        route_filter = indicator_df["route_id"] == route_id

        route_index_list = list(indicator_df[route_filter].index)

        observation_count = len(route_index_list)

        if (
            (sufficient_routes and observation_count < 6)
            or
            (not sufficient_routes and observation_count < 12)
        ):
            continue

        min_index = min(route_index_list)
        max_index = max(route_index_list)
        center_index = min_index + np.floor((max_index - min_index) / 2)

        if not sufficient_routes:
            analysis_index_list.extend([
                min_index, min_index + 1, min_index + 2, min_index + 3,
                center_index - 1, center_index, center_index + 1, center_index + 2, 
                max_index - 3, max_index - 2, max_index - 1, max_index
            ])   

        else:
            analysis_index_list.extend([
                min_index, min_index + 1, 
                center_index, center_index + 1, 
                max_index - 1, max_index
            ])                        

    return indicator_df.iloc[analysis_index_list]



def main():  
    counter = 0

    species_list = get_species_list()

    rng = np.random.default_rng(42)

    sample_frames = []
    a1_frames = []
    a11_frames = []

    while (len(sample_frames) < 30) or (len(a1_frames) < 30) or (len(a11_frames) < 20):
        sample_species_list = rng.choice(
            species_list,
            size=1,
            replace=False
        )

        for species_id in sample_species_list:
            counter += 1

            print("=" * 60)
            print(f"Durchlauf Nummer: {counter}\n")

            species_id_str = str(species_id).zfill(5)

            try:
                analysis_df = get_species_analysis_frame(species_id_str)
                sufficient_routes = analysis_df.loc[0, "sufficient_routes"] == 1

            except:
                print("Keine Datei")
                continue

            analysis_df = analysis_df.dropna(subset=INDICATOR_LIST).reset_index(drop=True)

            analysis_df = reduce_analysis_frame(analysis_df)

            if analysis_df.shape[0] >= 60:
                if len(sample_frames) < 30: 
                    sample_frames.append(analysis_df)

                if sufficient_routes and len(a1_frames) < 30:
                    a1_frames.append(analysis_df)

                if not sufficient_routes and len(a11_frames) < 30:        
                    a11_frames.append(analysis_df)

                print(
                    f"Samples: {len(sample_frames)} | "
                    f"A1: {len(a1_frames)} | "
                    f"A1.1Samples: {len(a11_frames)}\n"
                )

            else: 
                print("Frame zu kurz.\n")
                    
            species_list.remove(species_id)


    result_frames = {
        "sample_df": pd.concat(sample_frames, ignore_index=True),
        "a1_df": pd.concat(a1_frames, ignore_index=True), 
        "a11_df": pd.concat(a11_frames, ignore_index=True)
    }

    for frame_name, frame in result_frames.items():
        path = f"{DISTRIBUTION_FILES_DIR}/{frame_name}.csv"

        frame.to_csv(path, index=False)

# ================================================

if __name__ == "__main__":
    main()