import pandas as pd
import json 
from zipfile import ZipFile
from pathlib import Path

SPECIES_ZIP_PATH = "data/processed/species_csv_files.zip"
CLIMATE_CONFIG_PATH = "src/config/climate_config.json" 

INDICATORS = {
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
}

VARIABLE_INFO = {
    "temperature": {
        "unit": "°C",
        "decimals": 1
    },
    "precipitation": {
        "unit": "mm",
        "decimals": 0
    },
    "snowfall": {
        "unit": "mm",
        "decimals": 0
    },
    "wind_magnitude": {
        "unit": "m/s",
        "decimals": 2
    },
    "relative_humidity": {
        "unit": "%",
        "decimals": 1
    },
    "soil_moisture": {
        "unit": "m³/m³",
        "decimals": 3
    },
    "solar_flux_density": {
        "unit": "W/m²",
        "decimals": 0
    },
    "vegetation_coeff": {
        "unit": None,
        "decimals": 2
    }
}

def create_climate_config ():
    file_path = Path(CLIMATE_CONFIG_PATH)
    if file_path.exists():
        with open(CLIMATE_CONFIG_PATH, "r") as file:
            config = json.load(file)
        checked_files_list = config["meta_data"]["checked_files_list"]
    else: 
        config = {
            "meta_data": {},
            "variables": {}
        }
        checked_files_list = []
    
    climate_variables = {}

    config_variables = config["variables"]

    for variable, indicator_list in INDICATORS.items():
        climate_variables[variable] = []
        for indicator in indicator_list:
            climate_variables[variable].append(f"{variable}_{indicator}")

    with ZipFile(SPECIES_ZIP_PATH, "r") as zip:
        filenames = zip.namelist()
    
        files_count = len(filenames)
        counter = 0

        for species_id in filenames:
            counter += 1
            print(f"{counter}/{files_count} - Verarbeite: {species_id}")

            if species_id in checked_files_list:
                continue

            with zip.open(species_id) as file:
                species_df = pd.read_csv(file, encoding="utf-8")

            for variable, indicator_list in climate_variables.items():
                variable_dict = config_variables.setdefault(variable, {})

                for indicator in indicator_list:
                    values = pd.to_numeric(
                        species_df[indicator],
                        errors="coerce"
                    ).dropna()

                    if values.empty:
                        continue

                    minimum = values.quantile(0.05)
                    maximum = values.quantile(0.95)

                    if indicator not in variable_dict:
                        variable_dict[indicator] = {
                            "min": float(minimum),
                            "max": float(maximum)
                        }
                    else:
                        indicator_dict = variable_dict[indicator]

                        indicator_dict["min"] = min(
                            indicator_dict["min"],
                            float(minimum)
                        )

                        indicator_dict["max"] = max(
                            indicator_dict["max"],
                            float(maximum)
                        )

            checked_files_list.append(species_id)
            config["meta_data"]["checked_files_list"] = checked_files_list

            with open(CLIMATE_CONFIG_PATH, "w") as file:
                json.dump(config, file, ensure_ascii=True, indent=4)

    for variable, variable_dict in config_variables.items():
        for indicator, indicator_dict in variable_dict.items():
            range = indicator_dict["range"] = indicator_dict["max"] - indicator_dict["min"]

            indicator_dict["low_value_cap"] = indicator_dict["min"] + (range / 3)
            indicator_dict["high_value_cap"] = indicator_dict["min"] + 2 * (range / 3)

            for variable, variable_dict in VARIABLE_INFO.items():
                if variable in indicator:
                    indicator_dict["unit"] = variable_dict["unit"]
                    indicator_dict["round_decimals"] = variable_dict["decimals"]
                    break

    with open(CLIMATE_CONFIG_PATH, "w") as file:
        json.dump(config, file, ensure_ascii=True, indent=4)


if __name__ == "__main__":
    create_climate_config()