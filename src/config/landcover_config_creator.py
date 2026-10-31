import pandas as pd
import math
import json 

BBS_NLCD_PATH = "data/processed/full_bbs_landcover.csv"

LANDCOVER_CONFIG_PATH = "src/config/landcover_config.json"

LANDCOVER_VARIABLES = [
    "water", "developed", "barren", "forest", "shrubland",
    "grassland", "pasture", "cropland", "wetland"
]

def create_landcover_bins(values):
        
    min_value = values.min()
    max_value = values.max()

    q05 = values.quantile(0.05)
    q95 = values.quantile(0.95)

    z = q95 - q05
    decimals_z = max(1, -math.floor(math.log10(z/10)))

    pre_bins = [
        min_value,
        q05,
        q05 + 0.1 * z,
        q05 + 0.2 * z,
        q05 + 0.3 * z,
        q05 + 0.4 * z,
        q05 + 0.5 * z,
        q05 + 0.6 * z,
        q05 + 0.7 * z,
        q05 + 0.8 * z,
        q05 + 0.9 * z,
        q95,
        max_value
    ]

    bins = []

    for pre_bin in pre_bins:
        if pre_bin == 0:
            bin = 0

        else:
           bin = round(pre_bin, decimals_z)
           
        if not bin in bins:
            bins.append(bin)

    labels = [f"< {bins[1]} %"]

    for i in range(1, len(bins) - 2):
        labels.append(f"{bins[i]}-{bins[i+1]} %") 

    labels.append(f"> {bins[len(bins) - 2]} %")

    return bins, labels


def create_landcover_config ():
    df = pd.read_csv(BBS_NLCD_PATH, encoding="utf-8")

    config = {}

    for variable in LANDCOVER_VARIABLES:
        print("=" * 60)
        print(variable)

        values = df[variable] * 100
        bins, labels = create_landcover_bins(values)

        bin_dict = {
            "bins": bins,
            "labels": labels
        }

        config[variable] = {
            "binning_info": bin_dict
        }

    with open(LANDCOVER_CONFIG_PATH, "w") as file:
        json.dump(config, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    create_landcover_config()