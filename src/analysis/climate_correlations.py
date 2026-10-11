import pandas as pd
import numpy as np
import json
from zipfile import ZipFile
from src.analysis.correlate import check_low_deviation
from src.analysis.variable_preparations import bin_high_climate_variable_values
from src.visualization.prepare_visualization import get_model, get_model_curves

CLIMATE_CONFIG_PATH = "src/config/climate_config.json"
SPECIES_ZIP_PATH = "data/processed/species_csv_files.zip"
SPECIES_CONFIG_PATH = "src/config/species_config.json"


INDICATORS = {
    "temperature": ["mean", "min", "max", "std"],
    "precipitation": ["sum"],
    "wind_magnitude": ["mean"],
    "relative_humidity": ["mean", "min", "max", "std"],
    "soil_moisture": ["mean", "min", "max", "std"],
    "solar_flux_density": ["mean"],
    "vegetation_coeff": ["mean"]
}

def calculate_ranges(base_df, indicator):
    binned_df, min_bin_value, max_bin_value = bin_high_climate_variable_values(base_df, indicator)
    
    bin_count = binned_df.shape[0]
    relevance_threshold = 0.5 / bin_count

    if bin_count < 10:
        model, model_type, optimum = None, None, None

    else:
        model, model_type, optimum = get_model(binned_df["bin_value"], binned_df["proportion"])
    
    if model: 
        x_curve, y_curve = get_model_curves(model, model_type, min_bin_value, max_bin_value)

        relevant = y_curve >= relevance_threshold
        relevance_range = (x_curve[relevant].min(), x_curve[relevant].max())

        if optimum:
            y_optimum = np.interp(optimum, x_curve, y_curve)
            preferred = y_curve >= 0.8 * y_optimum
            preference_range = (x_curve[preferred].min(), x_curve[preferred].max())            
            
        else:
            preference_range = None

    else:
        relevance_filter = binned_df["proportion"] >= relevance_threshold
        relevant_binned_df = binned_df[relevance_filter].copy()

        relevance_range = (relevant_binned_df["bin_value"].min(), relevant_binned_df["bin_value"].max())
        preference_range = None

    return relevance_range, preference_range, optimum


def prepare_and_check_dataframe (base_df, indicator):
    analysis_df = base_df[["species_total", indicator]].copy()
    no_null_filter = analysis_df["species_total"].notna() & analysis_df[indicator].notna()
    analysis_df = analysis_df[no_null_filter]

    if not check_low_deviation(analysis_df[indicator]):
        return analysis_df
    

def get_preference_dictionary (base_df, indicator, max_range, low_value_cap, high_value_cap):
    analysis_df = prepare_and_check_dataframe(base_df, indicator)

    if not isinstance(analysis_df, pd.DataFrame):
        return

    relevance_range, preference_range, optimum = calculate_ranges(analysis_df, indicator)

    relevance_range_abs = relevance_range[1] - relevance_range[0]

    preference_range_abs = (
        preference_range[1] - preference_range[0]
        if preference_range
        else None
    )

    if preference_range_abs:
        range_type = "narrow" if preference_range_abs / max_range < 0.25 else "wide"
    else:
        range_type = "narrow" if relevance_range_abs / max_range < 0.5 else "wide"

    optimum_type = (
        None if optimum is None
        else "low" if optimum < low_value_cap
        else "high" if optimum > high_value_cap
        else "medium"
    )

    return {
        "relevance_range": relevance_range,
        "preference_range": preference_range,
        "optimum": optimum,
        "range_type": range_type,
        "optimum_type": optimum_type
    }


def calculate_climate_correlations():
    with open(CLIMATE_CONFIG_PATH, "r") as file:
        climate_config = json.load(file)

    all_variable_config = climate_config["variables"]

    with open(SPECIES_CONFIG_PATH, "r") as file:
        species_config = json.load(file)

    species_count = len(species_config)
    counter = 0
    
    for species_id, species_dict in species_config.items():
        counter += 1

        print("=" * 60)
        print(f"{counter}/{species_count} - Verarbeite: {species_dict['common_name']}")

        if "climate_preferences" in species_dict:
            continue

        filename = f"{species_id}.csv"

        with ZipFile(SPECIES_ZIP_PATH, "r") as zip:
            with zip.open(filename) as file:
                species_df = pd.read_csv(file, encoding="utf-8")

        climate_preferences = species_dict["climate_preferences"] = {}

        for variable_group, indicator_prefix_list in INDICATORS.items():
            print(variable_group)

            variable_config = all_variable_config[variable_group]

            variable_group_dict = climate_preferences[variable_group] = {}

            for indicator_prefix in indicator_prefix_list:
                prefix_dict = variable_group_dict[indicator_prefix] = {
                    "main": {},
                    "secondary": {}
                }

                main_indicator = f"{variable_group}_{indicator_prefix}_year"
                secondary_indicators = [
                    f"{variable_group}_{indicator_prefix}_{season}" 
                    for season in ["spring", "summer", "fall"]
                ]

                main_max_range = variable_config[main_indicator]["max"] - variable_config[main_indicator]["min"]

                low_value_cap = variable_config[main_indicator]["low_value_cap"]
                high_value_cap = variable_config[main_indicator]["high_value_cap"]

                main_preference_dict = get_preference_dictionary(
                    species_df, 
                    main_indicator, 
                    main_max_range, 
                    low_value_cap, 
                    high_value_cap
                )

                if not main_preference_dict:
                    continue

                prefix_dict["main"][main_indicator] = main_preference_dict

                main_range_type = main_preference_dict["range_type"]

                if main_range_type == "narrow":
                    continue

                for indicator in secondary_indicators:
                    max_range = variable_config[indicator]["range"]
                    low_value_cap = variable_config[main_indicator]["low_value_cap"]
                    high_value_cap = variable_config[main_indicator]["high_value_cap"]
                    
                    preference_dict = get_preference_dictionary(species_df, indicator, max_range, low_value_cap, high_value_cap)
    
                    if not preference_dict or preference_dict["range_type"] == "wide":
                        continue

                    prefix_dict["secondary"][indicator] = preference_dict

        with open(SPECIES_CONFIG_PATH, "w") as file:
            json.dump(species_config, file, ensure_ascii=False, indent=4)

def delete_climate_preferences():
    with open(SPECIES_CONFIG_PATH, "r") as file:
        species_config = json.load(file)
    
    for species_dict in species_config.values():
        del species_dict["climate_preferences"]

    with open(SPECIES_CONFIG_PATH, "w") as file:
        json.dump(species_config, file, ensure_ascii=False, indent=4)

               
if __name__ == "__main__":
    calculate_climate_correlations()
    # delete_climate_preferences()