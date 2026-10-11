import json
import pandas as pd

SPECIES_CONFIG_PATH = "src/config/species_config.json"

with open(SPECIES_CONFIG_PATH, "r") as file:
    species_config = json.load(file)

developed_list = []


for species_id, species_dict in species_config.items():
    developed_preferences = species_dict["landcover_preferences"]["developed"]

    developed_list.append({
        "name": species_dict["audubon_info"]["common_name"],
        "value": developed_preferences["preference_mean"]
    })

df = pd.DataFrame(developed_list)

print(df["value"].max())