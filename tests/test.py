import json
import numpy as np

with open("src/config/species_config.json", "r") as file:
    species_config = json.load(file)

VARIABLE = "temperature"
INDICATOR_GROUP = "mean"

INDICATOR = f"{VARIABLE}_{INDICATOR_GROUP}_year"


