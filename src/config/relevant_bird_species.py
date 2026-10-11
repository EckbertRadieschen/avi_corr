import os
from dotenv import load_dotenv

import pandas as pd
from zipfile import ZipFile
import json
from sqlalchemy.engine import URL
from sqlalchemy import create_engine


load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")


DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=MYSQL_USER,
    password=MYSQL_PASSWORD,
    host=MYSQL_HOST,
    database=MYSQL_DATABASE
)

ENGINE = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


ZIP_PATH = "data/processed/species_csv_files.zip"
SPECIES_CONFIG_PATH = "src/config/species_config.json"
ROUTE_CONFIG_PATH = "src/config/route_config.json"
LANDCOVER_CONFIG_PATH = "src/config/landcover_config.json"

species_list = [
    '00040', '00060', '00070', '00530', '00540', 
    '00590', '00770', '01200', '01250', '01320', 
    '01350', '01370', '01390', '01400', '01420', 
    '01430', '01440', '01460', '01470', '01490', 
    '01670', '01720', '01900', '01960', '02000', 
    '02001', '02010', '02020', '02060', '02140', 
    '02210', '02240', '02250', '02300', '02490', 
    '02580', '02610', '02630', '02640', '02730', 
    '02881', '02890', '03000', '03050', '03080', 
    '03091', '03100', '03131', '03160', '03250', 
    '03260', '03290', '03310', '03370', '03390', 
    '03420', '03430', '03480', '03490', '03520', 
    '03600', '03680', '03750', '03780', '03870', 
    '03880', '03900', '03930', '03940', '04020', 
    '04021', '04050', '04060', '04090', '04120', 
    '04160', '04171', '04200', '04230', '04280', 
    '04430', '04440', '04470', '04520', '04560', 
    '04570', '04590', '04610', '04620', '04640', 
    '04650', '04660', '04661', '04670', '04680', 
    '04690', '04740', '04750', '04770', '04780', 
    '04840', '04860', '04880', '04900', '04910', 
    '04930', '04940', '04950', '04970', '04980', 
    '05010', '05011', '05060', '05070', '05080', 
    '05100', '05110', '05120', '05140', '05170', 
    '05180', '05190', '05210', '05290', '05330', 
    '05380', '05390', '05400', '05420', '05450', 
    '05460', '05470', '05480', '05491', '05520', 
    '05540', '05580', '05600', '05610', '05620', 
    '05630', '05660', '05780', '05810', '05830', 
    '05840', '05870', '05880', '05900', '05930', 
    '05950', '05960', '05970', '05980', '05990', 
    '06010', '06040', '06050', '06070', '06080', 
    '06100', '06110', '06120', '06130', '06140', 
    '06150', '06160', '06170', '06190', '06220', 
    '06240', '06270', '06280', '06290', '06291', 
    '06292', '06310', '06330', '06360', '06370', 
    '06390', '06410', '06420', '06450', '06460', 
    '06480', '06520', '06550', '06570', '06580', 
    '06590', '06620', '06630', '06670', '06680', 
    '06710', '06730', '06740', '06750', '06760', 
    '06770', '06790', '06800', '06810', '06830', 
    '06840', '06850', '06860', '06870', '06882', 
    '06883', '07000', '07020', '07030', '07040', 
    '07050', '07150', '07180', '07190', '07210', 
    '07221', '07222', '07240', '07250', '07270', 
    '07280', '07310', '07350', '07360', '07380', 
    '07480', '07490', '07510', '07540', '07550', 
    '07560', '07580', '07590', '07610', '07630', 
    '07660', '07680', '22860']

full_observation_query = """
    SELECT
        state_num * 1000 + CAST(route AS UNSIGNED) AS route_id,
        aou AS species_id,
        `year`,
        species_total
    FROM bird_observations
    WHERE rpid = 101
    ORDER BY route_id, `year`, species_id;
"""

def extract_species_list ():
    xs_count = 0
    s_count = 0
    m_count = 0
    l_count = 0
    xl_count = 0

    bird_species_list = []

    with ZipFile(ZIP_PATH, "r") as zip_file:
        for filename in zip_file.namelist():
            with zip_file.open(filename) as file:
                species_df = pd.read_csv(file, encoding="utf-8")

                species_id = filename.replace('.csv', '')
                bird_species_list.append(species_id)

                df_size = species_df.shape[0]
                print(
                    f"\n{species_id} | "
                    f"Anzahl Records: {df_size}"
                )

                if df_size < 150:
                    xs_count += 1
                elif df_size < 200:
                    s_count += 1
                elif df_size < 500:
                    m_count += 1
                elif df_size < 2000:
                    l_count +=1
                else:
                    xl_count +=1

    print("=" * 60)
    print(f"\nSehr kleine Dateien: {xs_count}")
    print(f"Kleine Dateien:      {s_count}")
    print(f"Mittelgroße Dateien: {m_count}")
    print(f"Große Dateien:       {l_count}")
    print(f"Sehr große Dateien:  {xl_count}\n")


    print("=" * 60)
    print(species_id)

def add_bird_observation_count_to_config():
    with open(SPECIES_CONFIG_PATH, "r") as file:
        species_config = json.load(file)

    for species_id, species_dict in species_config.items():
        filename = f"{species_id}.csv"

        with ZipFile(ZIP_PATH, "r") as zip:
            with zip.open(filename) as file:
                species_df = pd.read_csv(file, encoding="utf-8")

        species_dict["meta_data"] = {
            "total_observations": species_df.shape[0]
        }
            
    with open(SPECIES_CONFIG_PATH, "w") as file:
        json.dump(species_config, file, ensure_ascii=False, indent=4)


def add_high_count_cap_to_config():
    print("Import data from database...")
    observation_df = pd.read_sql(full_observation_query, ENGINE)

    print("Calculate route-internal Q80...")
    route_quantiles = (
        observation_df
        .groupby(["species_id", "route_id"])["species_total"]
        .quantile(0.8)
    )

    print("Calculate species-level Highcount Caps...")
    species_caps = route_quantiles.groupby(level="species_id").quantile(0.8)

    with open(SPECIES_CONFIG_PATH, "r") as file:
        species_config = json.load(file)

    for species_id, config in species_config.items():
        config["meta_data"]["high_count_cap"] = round(species_caps.loc[species_id])

    with open(SPECIES_CONFIG_PATH, "w") as file:
        json.dump(species_config, file, ensure_ascii=False, indent=4)


def add_route_list_to_config():
    with open(SPECIES_CONFIG_PATH, "r") as file:
        species_config = json.load(file)

    with open(ROUTE_CONFIG_PATH, "r") as file:
        route_config = json.load(file)

    for species_id, species_dict in species_config.items():
        print(f"Working on species {species_id}")
        
        route_list = []

        for route_id, route_dict in route_config.items():
            if route_dict["country"] == "Canada" or route_dict["state"] == "Alaska":
                continue

            high_count_dict = route_dict["high_count_ratios"]

            if species_id in high_count_dict:
                route_list.append(route_id)

        species_dict["meta_data"]["route_list"] = route_list

        with open(SPECIES_CONFIG_PATH, "w") as file:
            json.dump(species_config, file, ensure_ascii=False, indent=4)

def add_urbanization_type_to_config():
    with open(SPECIES_CONFIG_PATH, "r") as file:
        species_config = json.load(file)

    for species_dict in species_config.values():
        landcover_preferences = species_dict["landcover_preferences"]
        developed_dict = landcover_preferences["developed"]
        developed_range_type = developed_dict["range_type"]
        developed_optimum = developed_dict["preference_mean"]

        developed_dict["urbanization_type"] = (
            "high" if developed_optimum > 10
            else "mid" if developed_optimum > 3
            else "low"
        )

        developed_dict["urbanization_range"] = "adaptive" if developed_range_type == "wide" else "rigid"

    with open(SPECIES_CONFIG_PATH, "w") as file:
        json.dump(species_config, file, ensure_ascii=False, indent=4)


def add_water_need_to_config():
    with open(SPECIES_CONFIG_PATH, "r") as file:
        species_config = json.load(file)

    value_list = []

    for species_dict in species_config.values():
        landcover_preferences = species_dict["landcover_preferences"]
        water_dict = landcover_preferences["water"]

        value_list.append(water_dict["preference_mean"])

    water_min = min(value_list)
    water_max = max(value_list)

    for species_dict in species_config.values():
        landcover_preferences = species_dict["landcover_preferences"]
        water_dict = landcover_preferences["water"]
        water_optimum = water_dict["preference_mean"]
        water_optimum_normed = (water_optimum - water_min) / (water_max - water_min)

        water_dict["water_need"] = water_optimum_normed

    with open(SPECIES_CONFIG_PATH, "w") as file:
        json.dump(species_config, file, ensure_ascii=False, indent=4)


def add_habitat_type():
    with open(SPECIES_CONFIG_PATH, "r") as file:
        species_config = json.load(file)

    for species_dict in species_config.values():
        landcover_preferences = species_dict["landcover_preferences"]

        landcover_means = []
        
        for variable, variable_dict in landcover_preferences.items():
            if not variable in ["water", "developed"]:
                landcover_means.append((variable, variable_dict["preference_mean"]))

        total_means = sum(mean for _, mean in landcover_means)

        preferred_landcover_list = [variable for variable, mean in landcover_means if mean / total_means >= 1/3]

        species_dict["preferred_landcover_list"] = sorted(preferred_landcover_list)

    with open(SPECIES_CONFIG_PATH, "w") as file:
        json.dump(species_config, file, ensure_ascii=True, indent=4)

if __name__ == "__main__":
    # extract_species_list()
    # add_bird_observation_count_to_config()
    # add_high_count_cap_to_config()
    # add_route_list_to_config()
    add_urbanization_type_to_config()
    # add_water_need_to_config()
    # add_habitat_type()