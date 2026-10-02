import json
import numpy as np

with open("src/config/species_config.json", "r") as file:
    species_config = json.load(file)

value_list = []

for species_dict in species_config.values():
    measure_group_dict = species_dict["audubon_info"]["measurements"]

    for measure_dict in measure_group_dict.values():
        if measure_dict["length"]["upper"] > 100:
            print(species_dict["common_name"])


