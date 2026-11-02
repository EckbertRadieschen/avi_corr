import json

SPECIES_CONFIG_PATH = "src/config/species_config.json"
LANDCOVER_STATS_CONFIG_PATH = "src/config/landcover_stat_config.json"

def create_landcover_stats_config ():
    with open(SPECIES_CONFIG_PATH, "r") as file:
        species_config = json.load(file)

    landcover_stats_config = {
        "landcover_types": {},
        "water_access": {},
        "urbanization_tolerance": {}
    }

    landcover_types = landcover_stats_config["landcover_types"]
    water_access = landcover_stats_config["water_access"]
    urbanization_tolerance = landcover_stats_config["urbanization_tolerance"] 

    for species_id, species_dict in species_config.items():
        if species_dict["meta_data"]["total_observations"] < 250:
            continue

        common_name = species_dict["audubon_info"]["common_name"]
        preferred_landcover_list = species_dict["preferred_landcover_list"]
        species_water_need = species_dict["landcover_preferences"]["water"]["preference_mean"]
        species_urbanization_tolerance = species_dict["landcover_preferences"]["developed"]["preference_mean"]
        
        if len(preferred_landcover_list) == 0:
            continue

        preferred_landcover_list = list(map(lambda x: x.capitalize(), preferred_landcover_list))

        landcover_string = "-".join(preferred_landcover_list)

        if not landcover_string in landcover_types:
            landcover_types[landcover_string] = {
                "species_list": [species_id],
                "species_count": 1
            }

        else:
            landcover_types[landcover_string]["species_list"].append(species_id)
            landcover_types[landcover_string]["species_count"] += 1

        water_access[common_name] = species_water_need

        urbanization_tolerance[common_name] = species_urbanization_tolerance

    with open(LANDCOVER_STATS_CONFIG_PATH, "w") as file:
        json.dump(landcover_stats_config, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    create_landcover_stats_config()