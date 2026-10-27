import json
import pandas as pd

SPECIES_CONFIG_PATH = "src/config/species_config.json"

with open(SPECIES_CONFIG_PATH, "r") as file:
    species_config = json.load(file)

longest_author = ""
species_with_longest_author = ""

for species_id, species_dict in species_config.items():
    audubon_info = species_dict["audubon_info"]
    picture_author = audubon_info["picture"]["author"]

    if len(picture_author) > len(longest_author):
        longest_author = picture_author
        species_with_longest_author = audubon_info["common_name"]

print(species_with_longest_author)
print(longest_author)