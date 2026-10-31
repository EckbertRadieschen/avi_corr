from src.visualization.create_climate_bars import climate_bar

def visualize_species_bars(climate_config, climate_preferences):
    
    for variable, variable_dict in climate_preferences.items():
        variable_config = climate_config[variable]

        main_dict = list(variable_dict.values())[0]["main"]
    
        if len(main_dict) == 0:
            continue

        for indicator, indicator_dict in main_dict.items():
            indicator_config = variable_config[indicator]
        
            global_min = indicator_config["min"]
            global_max = indicator_config["max"]
            variable_unit = indicator_config["unit"] if not variable == "vegetation_coeff" else ""
            round_decimals = indicator_config["round_decimals"]
        
            relevance_range = indicator_dict["relevance_range"]
            preference_range = indicator_dict["preference_range"]
            optimum = indicator_dict["optimum"]

            climate_bar(
                name=variable,
                global_min=global_min,
                global_max=global_max,
                relevance_range=relevance_range,
                preference_range=preference_range,
                optimum=optimum,
                unit=variable_unit,
                decimals=round_decimals
            )
            

