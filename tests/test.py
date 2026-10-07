import json
import numpy as np

with open("src/config/species_config.json", "r") as file:
    species_config = json.load(file)

VARIABLE = "temperature"
INDICATOR_GROUP = "mean"

INDICATOR = f"{VARIABLE}_{INDICATOR_GROUP}_year"

value_list = []
missing_optima_list = []

for species_id, species_dict in species_config.items():
    climate_preferences = species_dict["climate_preferences"]
    indicator_dict = climate_preferences[VARIABLE][INDICATOR_GROUP]["main"][INDICATOR]
    optimum = indicator_dict["optimum"]
    
    if optimum is None:
        missing_optima_list.append(species_id)

    else:
        value_list.append(optimum)

min_value = min(value_list)
max_value = max(value_list)

q5 = np.quantile(value_list, 0.05)
q95 = np.quantile(value_list, 0.95)
iqr = q95 - q5
bin_range = iqr / 5

missing_optima = len(missing_optima_list)
relevant_species = len(species_config) - missing_optima

print(f"Range: {min_value} - {max_value}")
print(f"Missing Optima: {missing_optima}")
