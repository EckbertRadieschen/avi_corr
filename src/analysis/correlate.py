import os
from dotenv import load_dotenv

import pandas as pd
from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from scipy.stats import pearsonr, spearmanr

import time

# ============================================================
# 1. MySQL-Verbindung
# ============================================================

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

species_query = """
SELECT 
    DISTINCT species_id
FROM analysis_route_species_relevant
ORDER BY species_id;
"""

species_df = pd.read_sql(species_query, ENGINE)

species_list = species_df["species_id"].tolist()

print(f"{len(species_list)} Arten")

# =====================================================

query = """
SELECT
    o.*,

    e.temperature_mean_year,
    e.temperature_mean_spring,
    e.temperature_mean_summer,
    e.temperature_mean_fall,
    e.temperature_mean_winter,
    e.temperature_min_year,
    e.temperature_max_year,
    e.temperature_min_spring,
    e.temperature_max_spring,
    e.temperature_min_summer,
    e.temperature_max_summer,
    e.temperature_min_fall,
    e.temperature_max_fall,
    e.temperature_min_winter,
    e.temperature_max_winter,
    e.temperature_std_year,
    e.temperature_std_spring,
    e.temperature_std_summer,
    e.temperature_std_fall,
    e.temperature_std_winter,

    e.precipitation_sum_year,
    e.precipitation_sum_spring,
    e.precipitation_sum_summer,
    e.precipitation_sum_fall,
    e.precipitation_sum_winter,
    e.precipitation_max_month,

    e.snowfall_sum_year,
    e.snowfall_sum_spring,
    e.snowfall_sum_summer,
    e.snowfall_sum_fall,
    e.snowfall_sum_winter,
    e.snowfall_max_month,

    e.wind_magnitude_mean_year,
    e.wind_magnitude_mean_spring,
    e.wind_magnitude_mean_summer,
    e.wind_magnitude_mean_fall,
    e.wind_magnitude_mean_winter,
    e.wind_magnitude_max_year,

    e.relative_humidity_mean_year,
    e.relative_humidity_mean_spring,
    e.relative_humidity_mean_summer,
    e.relative_humidity_mean_fall,
    e.relative_humidity_mean_winter,
    e.relative_humidity_min_year,
    e.relative_humidity_max_year,
    e.relative_humidity_min_spring,
    e.relative_humidity_max_spring,
    e.relative_humidity_min_summer,
    e.relative_humidity_max_summer,
    e.relative_humidity_min_fall,
    e.relative_humidity_max_fall,
    e.relative_humidity_std_year,
    e.relative_humidity_std_spring,
    e.relative_humidity_std_summer,
    e.relative_humidity_std_fall,
    e.relative_humidity_std_winter,

    e.soil_moisture_mean_year,
    e.soil_moisture_mean_spring,
    e.soil_moisture_mean_summer,
    e.soil_moisture_mean_fall,
    e.soil_moisture_mean_winter,
    e.soil_moisture_min_year,
    e.soil_moisture_max_year,
    e.soil_moisture_min_spring,
    e.soil_moisture_max_spring,
    e.soil_moisture_min_summer,
    e.soil_moisture_max_summer,
    e.soil_moisture_min_fall,
    e.soil_moisture_max_fall,
    e.soil_moisture_min_winter,
    e.soil_moisture_std_year,
    e.soil_moisture_std_spring,
    e.soil_moisture_std_summer,
    e.soil_moisture_std_fall,
    e.soil_moisture_std_winter,

    e.solar_flux_density_mean_year,
    e.solar_flux_density_mean_spring,
    e.solar_flux_density_mean_summer,
    e.solar_flux_density_mean_fall,
    e.solar_flux_density_mean_winter,

    e.vegetation_coeff_mean_year,
    e.vegetation_coeff_mean_spring,
    e.vegetation_coeff_mean_summer,
    e.vegetation_coeff_mean_fall,
    e.vegetation_coeff_mean_winter,

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
LEFT JOIN era5_route_analysis AS e
    ON o.route_id = e.route_id AND o.`year` = e.`year`
LEFT JOIN nlcd_route_analysis AS n
    ON o.route_id = n.route_id AND o.`year` = n.`year`
WHERE o.species_id = %(species_id)s;
"""

results = []
counter = 1

for species_id in species_list:
    print(f"\n[{counter}/{len(species_list)}] {species_id}")
    counter += 1

    species_df = pd.read_sql(query, ENGINE, params={"species_id": species_id})

    for route_id in species_df["route_id"].unique():
        route_filter = species_df["route_id"] == route_id
        route_df = species_df.loc[route_filter].sort_values("year")

        while route_df.iloc[0]["species_total"] == 0:
            species_df = species_df.drop(route_df.index[0])
            route_df = route_df.iloc[1:]

        while route_df.iloc[-1]["species_total"] == 0:
            species_df = species_df.drop(route_df.index[-1])
            route_df = route_df.iloc[:-1]

        continuous_zeros = 0

        for value in route_df["species_total"]:
            if value == 0:
                continuous_zeros += 1
                
                if continuous_zeros >= 3:
                    break
            else:
                continuous_zeros = 0

        if continuous_zeros >= 3:
            species_df = species_df.drop(route_df.index)

     
    # ========================================================
    # Vorläufige Beispielkorrelation
    # ========================================================

    analysis_df = species_df.copy()

    x = analysis_df["species_total"]
    y = analysis_df["temperature_mean_year"]

    valid = x.notna() & y.notna()

    if valid.sum() >= 20:

        pearson_r, pearson_p = pearsonr(
            x[valid],
            y[valid]
        )

        spearman_rho, spearman_p = spearmanr(
            x[valid],
            y[valid]
        )

        results.append({
            "species": species_id,
            "category": "Climate",
            "variable_group": "Temperature",
            "indicator": "mean_year",
            "pearson_r": pearson_r,
            "pearson_p": pearson_p,
            "spearman_rho": spearman_rho,
            "spearman_p": spearman_p,
            "n": valid.sum()
        })


# ============================================================
# 5. Ergebnisse als DataFrame
# ============================================================

results_df = pd.DataFrame(results)

print()
print("=" * 60)
print(f"Korrelationen berechnet: {len(results_df):,}")
print("=" * 60)

print(results_df.head())


# ============================================================
# 6. CSV speichern
# ============================================================

results_df.to_csv(
    "avi_corr_correlations.csv",
    index=False
)

print("CSV gespeichert.")
