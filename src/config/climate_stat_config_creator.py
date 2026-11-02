import json
import numpy as np

SPECIES_CONFIG_PATH = "src/config/species_config.json"
CLIMATE_CONFIG_PATH = "src/config/climate_config.json"
CLIMATE_STAT_CONFIG_PATH = "src/config/climate_stat_config.json"

INDICATORS = {
    "temperature": ["mean", "mean_year"],
    "precipitation": ["sum", "sum_year"],
    "wind_magnitude": ["mean", "mean_year"],
    "relative_humidity": ["mean", "mean_year"],
    "soil_moisture": ["mean", "mean_year"],
    "solar_flux_density": ["mean", "mean_year"],
    "vegetation_coeff": ["mean", "mean_year"]
}

with open(CLIMATE_CONFIG_PATH, "r") as file:
    climate_config = json.load(file)

with open(SPECIES_CONFIG_PATH, "r") as file:
    species_config = json.load(file)

statistics_config = {}

for variable, list in INDICATORS.items():
    variable_dict = statistics_config[variable] = {
        "meta_data": {},
        "species_values": {}
    }

    variable_config = climate_config["variables"][variable]

    indicator_group = list[0]
    indicator = f"{variable}_{list[1]}"

    indicator_config = variable_config[indicator]

    unit = indicator_config["unit"]
    rounding_decimals = indicator_config["round_decimals"]

    value_list = []
    missing_optima_list = []

    for species_id, species_dict in species_config.items():
        if species_dict["meta_data"]["total_observations"] < 250:
            continue

        climate_preferences = species_dict["climate_preferences"]

        if (
            variable not in climate_preferences
            or indicator_group not in climate_preferences[variable]
            or indicator not in climate_preferences[variable][indicator_group]["main"]
        ):    
            continue

        indicator_dict = climate_preferences[variable][indicator_group]["main"][indicator]
        optimum = indicator_dict["optimum"]
        
        if optimum is None:
            missing_optima_list.append(species_id)

        else:
            value_list.append(optimum)

    meta_data = variable_dict["meta_data"]

    min_value = min(value_list)
    max_value = max(value_list)

    meta_data["min"] = np.floor(min_value * (10 ** rounding_decimals)) / (10 ** rounding_decimals)
    meta_data["max"] = np.ceil(max_value * (10 ** rounding_decimals)) / (10 ** rounding_decimals)
    meta_data["slider_step"] = 1 / (10 ** rounding_decimals)
    meta_data["unit"] = unit
    meta_data["rounding_decimals"] = rounding_decimals

    value_range = max_value - min_value
    bin_range = value_range / 5

    bin_caps = [
        min_value + bin_range * i
        for i in range (0, 6) 
    ]

    bin_strings = [
        f"{round(bin_caps[index], rounding_decimals)}-{round(bin_caps[index + 1], rounding_decimals)}{unit}" 
        for index in range (0, 5) 
    ]

    bin_names = ["very low", "low", "mid", "high", "very high"]

    missing_optima = len(missing_optima_list)
    relevant_species = len(species_config) - missing_optima

    species_values = variable_dict["species_values"]

    for species_id, species_dict in species_config.items():
        if species_dict["meta_data"]["total_observations"] < 250:
            continue

        common_name = species_dict["audubon_info"]["common_name"]
        climate_preferences = species_dict["climate_preferences"]

        if (
            species_id in missing_optima_list
            or variable not in climate_preferences
            or indicator_group not in climate_preferences[variable]
            or indicator not in climate_preferences[variable][indicator_group]["main"]
        ):    
            continue

        indicator_dict = climate_preferences[variable][indicator_group]["main"][indicator]
        optimum = indicator_dict["optimum"]
        range_type = indicator_dict["range_type"]
        preference_range = indicator_dict["preference_range"]
        preference_lower = preference_range[0]
        preference_upper = preference_range[1]

        for cap, name, string in zip(bin_caps[1:], bin_names, bin_strings):
            if optimum <= cap:
                preference_type = name
                type_bin = string
                break

        species_values[species_id] = {
            "common_name": common_name,
            "optimum": optimum,
            "variable_preference": preference_type,
            "preference_range_width": preference_upper - preference_lower,
            "preference_type_bin": type_bin,
            "range_type": range_type
        }

with open(CLIMATE_STAT_CONFIG_PATH, "w") as file:
    json.dump(statistics_config, file, ensure_ascii=True, indent=4)
        
        
        

