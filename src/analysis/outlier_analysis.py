import json
import pandas as pd
from zipfile import ZipFile

SPECIES_ZIP_PATH = "data/processed/species_csv_files.zip"
SPECIES_CONFIG_PATH = "src/config/species_config.json"

def classify_count_value(value):
    bounds = [101, 182, 275, 720, 1738, 6282, 11726, 20187, 20985]
    for i in range(1, len(bounds)):
        if value <= bounds[i]:
            return f"{bounds[i-1]}-{bounds[i]}"

with open(SPECIES_CONFIG_PATH, "r") as file:
    species_config = json.load(file)

count_0 = 0
count_50 = 0
count_100 = 0
count_200 = 0
count_300 = 0
count_400 = 0
count_500 = 0

for species_id, species_dict in species_config.items():
    filename = f"{species_id}.csv"
    
    common_name = species_dict["audubon_info"]["common_name"]

    with ZipFile(SPECIES_ZIP_PATH, "r") as zip:
        with zip.open(filename) as file:
            species_df = pd.read_csv(file, encoding="utf-8")

    for row in species_df[["species_id", "species_total"]].itertuples():
        total = row[2]

        if total > 500:
            count_500 += 1
        elif total > 400:
            count_400 +=1
        elif total > 300:
            count_300 +=1
        elif total > 200:
            count_200 += 1
        elif total > 100:
            count_100 += 1
        elif total > 50:
            count_50 +=1
        else:
            count_0 +=1

print(f"Over 500: {count_500}")
print(f"400-500:  {count_400}")
print(f"300-400:  {count_300}")
print(f"200-300:  {count_200}")
print(f"100-200:  {count_100}")
print(f"50-100:   {count_50}")
print(f"0-50:     {count_0}")