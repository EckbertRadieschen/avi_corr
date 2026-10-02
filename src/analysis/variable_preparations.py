import pandas as pd
import numpy as np
import re
import json
from helpers import build_range_string, extract_bin_caps_from_label, get_landcover_variable_range
from zipfile import ZipFile
from typing import Literal

LANDCOVER_CONFIG_PATH = "src/config/landcover_config.json"
SPECIES_ZIP_PATH = "data/processed/species_csv_files.zip"
SPECIES_CONFIG_PATH = "src/config/species_config.json"

LANDCOVER_INDICATORS = [
    "water", "developed", "barren", "forest", "shrubland",
    "grassland", "pasture", "cropland", "wetland"
]

def bin_high_climate_variable_values(species_df: pd.DataFrame, variable_column: str, count_column="species_total"):

    analysis_df = species_df[[variable_column, count_column]].copy()

    threshold = analysis_df[count_column].quantile(0.80)
    treshold_filter = analysis_df[count_column] >= threshold
    high_counts_df = analysis_df[treshold_filter].copy() 

    total_high_counts = len(high_counts_df)

    indicator_min = high_counts_df[variable_column].min()
    indicator_max = high_counts_df[variable_column].max()

    total_bins = 30 if total_high_counts > 100 else 15

    bin_width = (indicator_max - indicator_min) / total_bins 

    high_counts_df["bin"] = np.minimum(
        np.floor((high_counts_df[variable_column] - indicator_min) / bin_width).astype(int)
        , total_bins - 1
    )

    high_counts_df["bin_value"] = (
        indicator_min + (high_counts_df["bin"] + 0.5) * bin_width
    )

    bin_groups = high_counts_df.groupby("bin")

    bin_results = []

    for bin_number, group in bin_groups:
        n = len(group)

        bin_results.append({
            "bin": bin_number,
            "bin_value": group["bin_value"].iloc[0],
            "n": n,
            "proportion": n / total_high_counts
        })

    min_bin_value = high_counts_df["bin_value"].min()
    max_bin_value = high_counts_df["bin_value"].max()

    return pd.DataFrame(bin_results), min_bin_value, max_bin_value


def remove_variable_null_values (df: pd.DataFrame, column1: str, column2: str):
    no_null_values_filter = df[column1].notna() & df[column2].notna()
    return df[no_null_values_filter]

def get_extension_frame(
        base_df: pd.DataFrame, 
        result_df: pd.DataFrame, 
        variable_column: pd.Series, 
        extension_dict: dict[str, str|float], 
        type: Literal["left", "right"]
) -> pd.DataFrame:
    
    proportion = extension_dict["proportion"]
    boundary_bin_label = extension_dict["boundary_bin_label"]
    boundary_cap = extension_dict["boundary_cap"]
    extreme_value = extension_dict["extreme_value"]
    z = extension_dict["range"]


    result_df = result_df.drop(boundary_bin_label)

    boundary_df = base_df.copy()

    boundary_filter = (
        (boundary_df[variable_column] < boundary_cap) 
        if type == "left" 
        else (boundary_df[variable_column] > boundary_cap)
    )

    boundary_df = boundary_df[boundary_filter]
            
    if z != 0:
        bin_width = z / 3

        binning_start_value = extreme_value if type == "left" else boundary_cap

        bins = [binning_start_value + bin_width * i for i in range(0, 4)]

        cut = pd.cut(boundary_df[variable_column], bins=bins, include_lowest=True)

        extension_series = cut.value_counts(sort=False, normalize=True) * proportion
        extension_df = extension_series.to_frame()

        new_index_values = []

        for index_value in extension_df.index:
            stringified = re.sub(r"[\[\]\(\)\s]", "", str(index_value))

            caps = map(float, stringified.split(","))
            new_index_values.append(build_range_string(list(caps)) + " %")

        extension_df.index = new_index_values

        extension_df["origin"] = "lower" if type == "left" else "higher"
        extension_df.columns = ["proportion", "origin"]

        result_df = (
            pd.concat([extension_df, result_df])
            if type == "left"
            else pd.concat([result_df, extension_df])
        )

    return result_df
    


def get_extension_dicts(
        distribution_series: pd.Series, 
        global_variable_values: pd.Series, 
        bins: list[float], 
        labels: list[str]
) -> tuple[dict[str, str|float], dict[str, str|float]]:
    
    min_value = max(0, global_variable_values.min())
    max_value = min(100, global_variable_values.max())

    lower_boundary = bins[1]
    low_bin_label = labels[0]
    higher_boundary = bins[-2]
    high_bin_label = labels[-1]

    low_prop = distribution_series[low_bin_label]
    high_prop = distribution_series[high_bin_label]

    low_extension_dict = {
        "proportion": low_prop,
        "boundary_bin_label": low_bin_label,
        "boundary_cap": lower_boundary,
        "extreme_value" : min_value,
        "range": lower_boundary - min_value
        
    }

    high_extension_dict = {
        "proportion": high_prop,
        "boundary_bin_label": high_bin_label,
        "boundary_cap": higher_boundary,
        "extreme_value": max_value,
        "range": max_value - higher_boundary
    }

    return low_extension_dict, high_extension_dict


def get_landcover_high_count_distribution(species_df: pd.DataFrame, variable_column: str, count_column="species_total"):
    with open(LANDCOVER_CONFIG_PATH, "r") as file:
        config = json.load(file)

    species_df[variable_column] *= 100

    binning_info = config[variable_column]["binning_info"]

    threshold = species_df[count_column].quantile(0.80)
    treshold_filter = species_df[count_column] >= threshold
    high_counts = species_df[treshold_filter].copy() 

    variable_bins = binning_info["bins"]
    variable_labels = binning_info["labels"]

    high_counts["class"] = pd.cut(
        high_counts[variable_column],
        bins=variable_bins,
        labels=variable_labels,
        right=False
    )

    distribution_series = (
        high_counts["class"]
        .value_counts(sort=False, normalize=True)
        .reindex(variable_labels, fill_value=0)
    )

    raw_distribution_df = distribution_series.to_frame()
    raw_distribution_df["origin"] = "regular"
    raw_distribution_df.columns = ["proportion", "origin"]

    distribution_df = raw_distribution_df.copy()

    global_variable_values = species_df[variable_column]

    low_extension_dict, high_extension_dict = get_extension_dicts(
        distribution_series, 
        global_variable_values,
        variable_bins, 
        variable_labels  
    )

    if low_extension_dict["proportion"] > 0.05:
        distribution_df = get_extension_frame(high_counts, distribution_df, variable_column, low_extension_dict, "left")

    if high_extension_dict["proportion"] > 0.05:
        distribution_df = get_extension_frame(high_counts, distribution_df, variable_column, high_extension_dict, "right")

    return raw_distribution_df, distribution_df

# =====================================================================================================
# =====================================================================================================

def get_species_landcover_preferences():
    print("Start Preference Generator")

    with open(SPECIES_CONFIG_PATH, "r") as file:
        species_config = json.load(file)

    total_species = len(species_config)
    species_counter = 0

    for species_id, species_dict in species_config.items():
        species_counter += 1
        print(f"{species_counter}/{total_species} - {species_id}")

        if len(species_dict.get("landcover_preferences", {})) == 8:
            continue 

        filename = f"{species_id}.csv"

        preferences = species_dict["landcover_preferences"] = {}

        with ZipFile(SPECIES_ZIP_PATH, "r") as zip:
            with zip.open(filename) as file:
                species_df = pd.read_csv(file, encoding="utf-8")

        for variable_column in LANDCOVER_INDICATORS:
            print(f"    {variable_column}")

            variable_dict = preferences[variable_column] = {}

            raw_distribution, extended_distribution = get_landcover_high_count_distribution(species_df, variable_column)

            analysis_df = raw_distribution.copy()

            max_filter = analysis_df["proportion"] == analysis_df["proportion"].max()

            top_list = analysis_df.index[max_filter].to_list()

            top_group_cap = analysis_df.loc[top_list[0], "proportion"] * 0.8

            top_bin_filter = analysis_df["proportion"] >= top_group_cap

            top_bins = analysis_df.index[top_bin_filter].to_list()

            base_bins = []

            max_range, max_range_lowest_cap, max_range_highest_cap = get_landcover_variable_range(raw_distribution.index.to_list())
            max_bins = raw_distribution.shape[0]

            for bin in top_bins:
                if ">" in bin or "<" in bin:
                    analysis_df = extended_distribution.copy()
                    max_range, max_range_lowest_cap, _ = get_landcover_variable_range(extended_distribution.index.to_list())
                    max_bins = extended_distribution.shape[0]
                else:
                    base_bins.append(bin)


            low_extension_filter = (analysis_df["origin"] == "lower") & (analysis_df["proportion"] >= 0.05)
            low_extension_bins = analysis_df.index[low_extension_filter].to_list()
            
            high_extension_filter = (analysis_df["origin"] == "higher") & (analysis_df["proportion"] >= 0.05)
            high_extension_bins = analysis_df.index[high_extension_filter].to_list()

            analysis_bins = low_extension_bins + base_bins + high_extension_bins

            high_bins_df = analysis_df.copy().loc[analysis_bins]
            high_bins_df = high_bins_df.reset_index(names="label")

            high_bins_df["caps"] = high_bins_df["label"].apply(extract_bin_caps_from_label)
            high_bins_df["bin_mean"] = high_bins_df["caps"].apply(np.mean)

            preference_range, pref_range_low, pref_range_high = get_landcover_variable_range(list(high_bins_df["label"].values))
            variable_dict["preference_range"] = preference_range
            variable_dict["preference_lower_cap"] = pref_range_low
            variable_dict["preference_upper_cap"] = pref_range_high
                  
            pref_mean = variable_dict["preference_mean"] = (
                (high_bins_df["bin_mean"] * high_bins_df["proportion"]).sum() 
                / 
                high_bins_df["proportion"].sum()
            )

            left_type_cap = max_range_lowest_cap + max_range / 3
            right_type_cap = max_range_lowest_cap + max_range / 3

            if pref_mean < left_type_cap:
                preference_type = "low"
            elif pref_mean > right_type_cap:
                preference_type = "high"
            else:
                preference_type = "middle"

            variable_dict["preference_type"] = preference_type
            

            variable_dict["is_real_optimum"] = len(analysis_bins) / max_bins < 1/3

            relevant_filter = analysis_df["proportion"] >= 0.05
            relevant_bins_df = analysis_df.copy()[relevant_filter]
            relevant_bins_df = relevant_bins_df.reset_index(names="label")

            relevant_range, rel_range_low, rel_range_high = get_landcover_variable_range(list(relevant_bins_df["label"].values))
            variable_dict["range"] = relevant_range
            variable_dict["range_lower_cap"] = rel_range_low
            variable_dict["range_upper_cap"] = rel_range_high
            variable_dict["range_type"] = "wide" if relevant_range / max_range >= 0.5 else "narrow"

        with open(SPECIES_CONFIG_PATH, "w") as file:
            json.dump(species_config, file, ensure_ascii=False, indent=4)
            

def delete_landcover_preferences():
    with open(SPECIES_CONFIG_PATH, "r") as file:
        species_config = json.load(file)

    for  species_dict in species_config.values():
        if "landcover_preferences" in species_dict:
            del species_dict["landcover_preferences"]

    with open(SPECIES_CONFIG_PATH, "w") as file:
        json.dump(species_config, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    # get_species_landcover_preferences()
    # delete_landcover_preferences()
    pass