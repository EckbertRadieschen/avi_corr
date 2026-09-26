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
PSP_RESULT_URL = "data/processed/correlations_psp_regular.csv"
QUAD_RESULT_URL = "data/processed/correlations_quad_regular.csv"

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

    return species_df["species_id"].tolist()

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
    


def check_low_deviation (x: pd.Series):
    mean = x.mean()
    std = x.std()
    lower = mean - 0.5 * std
    upper = mean + 0.5 * std

    sigma_counter = 0

    for value in x:
        if lower <= value <= upper:
            sigma_counter += 1

    return sigma_counter / len(x) > 0.6

def correlate_pearson_spearman (x: pd.Series, y: pd.Series):                
    pearson_r, pearson_p = pearsonr(x, y)
    spearman_rho, spearman_p = spearmanr(x, y)

    return  {
        "pearson_r": pearson_r,
        "pearson_p": pearson_p,
        "spearman_rho": spearman_rho,
        "spearman_p": spearman_p
    }

def correlate_quadratic (x: pd.Series, y: pd.Series):
    df = pd.concat([x, y], axis=1)
    df.columns = ["x", "y"]
    df["x_squared"] = df["x"] ** 2

    X = df[["x", "x_squared"]]
    X = sm.add_constant(X)
    Y = df["y"]

    model = sm.GLM(y, X, family=sm.families.NegativeBinomial())

    result = model.fit()

    beta0 = result.params["const"]
    beta1 = result.params["x"]
    beta2 = result.params["x_squared"]

    se_beta1 = result.bse["x"]
    se_beta2 = result.bse["x_squared"]
    p_beta1 = result.pvalues["x"]
    p_beta2 = result.pvalues["x_squared"]  

    rsquared = result.rsquared
    rsquared_adj = result.rsquared_adj
    f_pvalue = result.f_pvalue

    optimum = -beta1 / (2 * beta2)
    optimum_in_range = x.min() <= optimum <= x.max()

    return {
        "beta0": beta0,
        "beta1": beta1,
        "beta2": beta2,
        "se_beta1": se_beta1,
        "se_beta2": se_beta2,
        "p_beta1": p_beta1,
        "p_beta2": p_beta2,
        "rsquared": rsquared,
        "rsquared_adj": rsquared_adj,
        "f_pvalue": f_pvalue,
        "optimum": optimum,
        "optimum_in_range": optimum_in_range
    }
    
def main():  
    psp_results = []
    quad_results = []
    counter = 0

    species_list = get_species_list()

    for species_id in species_list:
        counter += 1

        species_id_str = str(species_id).zfill(5)
        print(f"[{counter}/{len(species_list)}] - {species_id_str}")

        try:
            analysis_df = get_species_analysis_frame(species_id_str)

        except:
            print("Keine Datei")
            continue

        sufficient_routes = analysis_df.loc[0, "sufficient_routes"] == 1

        for category, variable_dict in INDICATORS.items():
            for variable, indicator_methods in variable_dict.items():
                for indicator_method in indicator_methods:
                    indicator = f"{variable}_{indicator_method}" if indicator_method else variable

                    indicator_df = analysis_df.copy()

                    complete_values = indicator_df[indicator].notna() & indicator_df["species_total"].notna()

                    indicator_df = indicator_df[complete_values].sort_values(["route_id", "year"]).reset_index(drop=True)

                    indicator_df = reduce_analysis_frame(indicator_df)
                    valid_records = indicator_df.shape[0]

                    x = indicator_df[indicator]
                    y = indicator_df["species_total"]

                    if valid_records < 60:
                        continue

                    result = {
                        "species": species_id,
                        "category": category,
                        "variable": variable,
                        "indicator": indicator_method,
                        "n": valid_records,
                        "few_routes": not sufficient_routes 
                    }

                    if check_low_deviation(x): 
                        continue

                    psp_dict = correlate_pearson_spearman(x, y)
                    sp_rho = psp_dict["spearman_rho"]


                    if  abs(sp_rho) >= 0.3:
                        result.update(psp_dict)
                        psp_results.append(result)
                        continue

                    quad_dict = correlate_quadratic(x, y)

                    if (
                        quad_dict["p_beta2"] < 0.05
                        and quad_dict["beta2"] < 0
                        and quad_dict["rsquared"] > 0.1
                        and quad_dict["optimum_in_range"]
                    ):
                        result.update(quad_dict)
                        quad_results.append(result)

    psp_results_df = pd.DataFrame(psp_results)
    quad_results_df = pd.DataFrame(quad_results)

    psp_results_df.to_csv(PSP_RESULT_URL, index=False)
    quad_results_df.to_csv(QUAD_RESULT_URL, index=False)
    
    print("Fertig!")

if __name__ == "__main__":
    main()