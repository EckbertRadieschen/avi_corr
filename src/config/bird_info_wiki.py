import os
from dotenv import load_dotenv

import requests
import json
from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from bs4 import BeautifulSoup

import pandas as pd
import time
import re
from zipfile import ZipFile

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

BIRD_QUERY = """
    SELECT DISTINCT
        species_id,
        scientific_name,
        common_name,
        `order`,
        family,
        genus
    FROM analysis_species_list
    ORDER BY species_id;
"""

WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
HEADERS = {
    "User-Agent": "AviCorr/1.0 (Wikipedia species information project)"
}

AUDUBON_BASE_URL = "https://www.audubon.org"
AUDUBON_GUIDE_URL = "https://www.audubon.org/bird-guide"

SPECIES_CONFIG_PATH = "src/config/species_config.json"
SPECIES_ZIP_PATH = "data/processed/species_csv_files.zip"

def build_bird_config ():
    species_df = pd.read_sql(BIRD_QUERY, ENGINE)

    with ZipFile(SPECIES_ZIP_PATH, "r") as zip:
        filenames= zip.namelist()

    relevant_species_list = [filename.replace(".csv", "") for filename in filenames]

    species_df = species_df.set_index("species_id").loc[relevant_species_list]

    species_json = {}

    for species_id in species_df.index:

        species_json[species_id] = {
            "scientific_name": species_df.loc[species_id, "scientific_name"],
            "common_name": species_df.loc[species_id, "common_name"],
            "order": species_df.loc[species_id, "order"],
            "family": species_df.loc[species_id, "family"],
            "genus": species_df.loc[species_id, "genus"]
        }

    with open(SPECIES_CONFIG_PATH, "w", encoding="utf-8") as file:
        json.dump(species_json, file, ensure_ascii=False, indent=4)



def get_wikipedia_urls ():
    
    with open(SPECIES_CONFIG_PATH, "r", encoding="utf-8") as file:
        species_json = json.load(file)

    for species_dict in species_json.values():
        if "url" in species_dict.keys():
            continue

        name = species_dict["scientific_name"]

        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": name,
            "srlimit": 1
        }

        print(f"Hole URL für {name}")

        response = requests.get(WIKIPEDIA_API, params=params, headers=HEADERS)

        if response.status_code == 429:
            return int(response.headers.get("Retry-After", 5))

        response.raise_for_status()

        data = response.json()
        results = data["query"]["search"]

        if results:
            title = results[0]["title"]
            wiki_url = "https://en.wikipedia.org/wiki/" + title.replace(" ", "_")
            
            species_dict["url"] = wiki_url

        else:
            species_dict["url"] = None

        time.sleep(1)

        with open(SPECIES_CONFIG_PATH, "w", encoding="utf-8") as file:
            json.dump(species_json, file, ensure_ascii=False, indent=4)


def get_audubon_lazy_cards (ids):
    load_url = f"https://www.audubon.org/birds-cards/lazy-load/en/{','.join(map(str, ids))}?v=1"

    response = requests.get(load_url, headers=HEADERS)
    response.raise_for_status()

    cards = []

    commands = response.json()

    for command in commands:
        if command.get("command") == "applyBirdCards":
            for data in command.get("data", []):
                cards.append({
                    "id": data.get("id"),
                    "scientific": data.get("scientific"),
                    "common_name": data.get("title"),
                    "family": data.get("family"),
                    "url": data.get("url"),
                    "description": data.get("description"),
                    "status": data.get("status"),
                    "habitats": data.get("habitats")
                })
    return cards

def get_audubon_urls ():
    with open(SPECIES_CONFIG_PATH, "r", encoding="utf-8") as file:
        species_json = json.load(file)

    species_map = {}
    
    for species_id, species_dict in species_json.items():
        scientific_name = species_dict["scientific_name"]

        species_map[scientific_name] = species_id

    response = requests.get(AUDUBON_GUIDE_URL, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    cards = soup.select("div.bird-card-2023")

    lazy_ids = [
        card["data-id"]
        for card in cards 
        if any("lazyload" in part_class for part_class in card["class"])
    ]

    n = len(lazy_ids)

    lazy_id_chunks = [lazy_ids[i:i+8] for i in range(0, n, 8)]

    info_card_list = []

    for card in cards:
        if card["data-id"] in lazy_ids:
            continue

        else:
            data_id = card.get("data-id")
            audubon_common_name = card.select_one(".bird-card-title").get_text(strip=True)
            audubon_scientific_name = card.select_one(".bird-card-scientific").get_text(strip=True)
            audubon_species_url = f"{AUDUBON_BASE_URL}{card.select_one('a.card-link')['href']}"

            info_card_list.append({
                "data_id": data_id,
                "common_name": audubon_common_name,
                "scientific_name": audubon_scientific_name,
                "species_url": audubon_species_url
            })

    for i, chunk in enumerate(lazy_id_chunks, start=1):
        cards = get_audubon_lazy_cards(chunk)

        for card in cards:
            info_card_list.append({
                "data_id": card["id"],
                "common_name": card["common_name"],
                "scientific_name": card["scientific"],
                "species_url": f"{AUDUBON_BASE_URL}{card['url']}"
            })

        print(f"Chunk {i}/{len(lazy_id_chunks)} verarbeitet")
        
        if i < len(lazy_id_chunks):
            time.sleep(2)

    for card in info_card_list:
        audubon_scientific_name = card["scientific_name"]

        if not audubon_scientific_name in species_map:
            continue

        species_id = species_map[audubon_scientific_name]

        species_json[species_id]["audubon_info"] = {
            "data_id": card["data_id"],
            "common_name": card["common_name"],
            "species_url": card["species_url"]
        }

    missing_species = []
    
    for species_dict in species_json.values():
        if not "audubon_info" in species_dict:
            missing_species.append(species_dict["scientific_name"])

    with open(SPECIES_CONFIG_PATH, "w", encoding="utf-8") as file:
        json.dump(species_json, file, ensure_ascii=False, indent=4)

    print(missing_species)


def check_config_for_missing_urls():
    with open(SPECIES_CONFIG_PATH, "r", encoding="utf-8") as file:
        species_json = json.load(file)

    missing_urls = []

    for info in species_json.values():
        if info["url"] is None:
            missing_urls.append(info["common_name"])

    print(missing_urls)


def get_species_audubon_data ():
    print("=" * 60)
    print("Extract Audubon Data\n")

    with open(SPECIES_CONFIG_PATH, "r", encoding="utf-8") as file:
        species_json = json.load(file)

    species_to_go = 0

    for species_dict in species_json.values():
        if not "description" in species_dict["audubon_info"]:
            species_to_go += 1

    species_issues = []

    for number, (species_id, species_dict) in enumerate(species_json.items(), start=1):
        print(f"Verarbeite {species_dict['scientific_name']}: {number}/{species_to_go}")

        audubon_info = species_dict["audubon_info"]
        species_url = audubon_info["species_url"]

        if "description" in audubon_info:
            continue

        response = requests.get(species_url, headers=HEADERS)

        if response.status_code == 429:
            wait_time = int(response.headers.get("Retry-After", 5))
            return wait_time

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        try:
            blocks = ["div.bird_info_item.info_description", "div.bird-taxonomy.grid_type"]

            for block in blocks:
                block_item = soup.select_one(block)

                content_selector = block_item.select_one("div.content")

                if content_selector:
                    audubon_info["description"] = block_item.select_one("div.content").get_text(" ", strip=True)

                for item in block_item.select("div.tax-item"):
                    title = item.select_one("div.tax-title")
                    value = item.select_one("div.tax-value")

                    if title and value:
                        info_title = title.get_text(" ", strip=True)
                        info_value = value.get_text(" ", strip=True)

                        audubon_info[info_title] = info_value

            media_data_item = soup.select_one("div.media-data")
            image = media_data_item.select_one("img")
            
            image_source_set = image.get("srcset")
            image_url = str(image_source_set).split()[0].split("?")[0]

            image_title = image.get("title")

            image_author = str(image_title).split(":", maxsplit=1)[1].strip()

            audubon_info["picture"] = {
                "url": image_url,
                "author": image_author
            }

            with open(SPECIES_CONFIG_PATH, "w", encoding="utf-8") as file:
                json.dump(species_json, file, ensure_ascii=False, indent=4)

        except:
            species_issues.append(species_id)
            print(f"Problem-Count: {len(species_issues)}")
            continue


def requester(page):
    if page == "wikipedia":
        request_function = get_wikipedia_urls
    elif page == "audubon":
        request_function = get_species_audubon_data

    else: 
        print("Wrong Function Input")
        return

    while True:
        wait_time = request_function()

        if wait_time is None:
            break

        print(f"Rate Limit. Warte {wait_time} Sekunden...")
        time.sleep(wait_time)


def parse_measurement(measurement):
    measurement = measurement.strip()

    pattern = r"""
        (?P<lower>[\d.]+)
        \s*
        (?P<lower_unit>kg|g|cm|m)?
        \s*
        (?:
            [\-–—]
            \s*
            (?P<upper>[\d.]+)
            \s*
            (?P<upper_unit>kg|g|cm|m)?
        )?
    """

    match = re.fullmatch(pattern, measurement, re.VERBOSE)

    if not match:
        return {}

    lower = float(match.group("lower"))
    upper = match.group("upper")
    lower_unit = match.group("lower_unit")
    upper_unit = match.group("upper_unit")

    if upper is None:
        upper = lower
    else:
        upper = float(upper)

    if lower_unit is None and upper_unit is None:
        target_unit = None

    if lower_unit is None:
        lower_unit = upper_unit

    if upper_unit is None:
        upper_unit = lower_unit

    if lower_unit in ("g", "kg") and upper_unit in ("g", "kg"):
        target_unit = "g"
    elif lower_unit in ("cm", "m") and upper_unit in ("cm", "m"):
        target_unit = "cm"
    else:
        target_unit = None

    pre_measures = {
        "lower": {
            "value": float(lower),
            "unit": lower_unit
        },
        "upper": {
            "value": float(upper),
            "unit": upper_unit
        }
    }

    for measure_dict in pre_measures.values():
        unit = measure_dict["unit"]

        if target_unit == "g":
            if unit == "kg":
                measure_dict["value"] *= 1000

        if target_unit == "cm":
            if unit == "m":
                measure_dict["value"] *= 100

    return {
        "lower": pre_measures["lower"]["value"],
        "upper": pre_measures["upper"]["value"],
        "unit": target_unit
    }


def analyse_species_size_descriptions():
    with open(SPECIES_CONFIG_PATH, "r", encoding="utf-8") as file:
        species_json = json.load(file)

    missing_species = []

    for species_id, species_dict in species_json.items():
        audubon_info = species_dict["audubon_info"]
        description = audubon_info["description"]

        measurements = re.findall(
            r"\(([\d.\s\-–—]+(?:cm|m|g|kg)[\d.\s\-–—]*(?:cm|m|g|kg)?)\)",
            description
        )

        if len(measurements) < 3:
            missing_species.append(species_id)
            continue

        if len(measurements) == 3:
            measurement_dict = {
                "both_sexes": {
                    "length": parse_measurement(measurements[0]),
                    "wingspan": parse_measurement(measurements[1]),
                    "weight": parse_measurement(measurements[2])
                }
            }

        if len(measurements) == 6:
            measurement_dict = {
                "female": {
                    "length": parse_measurement(measurements[0]),
                    "wingspan": parse_measurement(measurements[1]),
                    "weight": parse_measurement(measurements[2])
                },
                "male": {
                    "length": parse_measurement(measurements[3]),
                    "wingspan": parse_measurement(measurements[4]),
                    "weight": parse_measurement(measurements[5])
                }           
            }           

        audubon_info["measurements"] = measurement_dict

        with open(SPECIES_CONFIG_PATH, "w", encoding="utf-8") as file:
            json.dump(species_json, file, ensure_ascii=False, indent=4)

    print()
    print(missing_species)

def clean_audubon_photo_author ():
    with open(SPECIES_CONFIG_PATH, "r") as file:
        species_config = json.load(file)
    
    for species_id, species_dict in species_config.items():
        audubon_info = species_dict["audubon_info"]
        picture_author = audubon_info["picture"]["author"]
    
        picture_author = audubon_info["picture"]["author"]

        if "Photo:" in picture_author:
            picture_author = picture_author.rsplit("Photo:", 1)[1].strip()

        if "(" in picture_author:
            picture_author = picture_author.rsplit("(", 1)[0].strip()

        if "/" in picture_author:
            picture_author = picture_author.rsplit("/", 1)[0].strip()

        audubon_info["picture"]["author"] = picture_author

    with open(SPECIES_CONFIG_PATH, "w") as file:
        json.dump(species_config, file, ensure_ascii=True, indent=4)

if __name__ == "__main__":
    # build_bird_config()
    # check_config_for_missing_urls()
    # get_audubon_urls()
    # requester("audubon")
    # analyse_species_size_descriptions()
    clean_audubon_photo_author()

    # problematic_species = [
    #     '01440', '01460', '01960', '02010', '02140', '02210', '02890', '03091', '03131', '03250', 
    #     '03290', '03310', '03390', '03490', '04060', '04160', '04680', '04780', '05070', '05170', 
    #     '05330', '05390', '05480', '05580', '05780', '05810', '05870', '05880', '05950', '06010', 
    #     '06070', '06080', '06110', '06130', '06140', '06270', '06291', '06292', '06550', '06882', 
    #     '07000', '07050', '07180', '07270', '07310', '07480', '07490', '07550'
    # ]

    # with open(SPECIES_CONFIG_PATH, "r", encoding="utf-8") as file:
    #     species_json = json.load(file)   

    # for species_id in problematic_species:
    #     species_dict = species_json[species_id]

    #     print(f"{species_id}: {species_dict['audubon_info']['common_name']}")