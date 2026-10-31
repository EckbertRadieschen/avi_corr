import pandas as pd
import numpy as np
import re
import json

from typing import Literal

from src.helpers import build_range_string
from src.analysis.correlate import check_low_deviation
from src.visualization.prepare_visualization import get_model, get_model_curves

LANDCOVER_CONFIG_PATH = "src/config/landcover_config.json"
SPECIES_ZIP_PATH = "data/processed/species_csv_files.zip"
SPECIES_CONFIG_PATH = "src/config/species_config.json"


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
            new_index_values.append(build_range_string(list(caps)).lstrip("-") + " %")

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


def calculate_ranges(base_df, indicator):
    binned_df, min_bin_value, max_bin_value = bin_high_climate_variable_values(base_df, indicator)
    
    bin_count = binned_df.shape[0]
    relevance_threshold = 0.5 / bin_count

    if bin_count < 10:
        model, model_type, optimum = None, None, None

    else:
        model, model_type, optimum = get_model(binned_df["bin_value"], binned_df["proportion"])
    
    if model: 
        x_curve, y_curve = get_model_curves(model, model_type, min_bin_value, max_bin_value)

        relevant = y_curve >= relevance_threshold
        relevance_range = (x_curve[relevant].min(), x_curve[relevant].max())

        if optimum:
            y_optimum = np.interp(optimum, x_curve, y_curve)
            preferred = y_curve >= 0.8 * y_optimum
            preference_range = (x_curve[preferred].min(), x_curve[preferred].max())            
            
        else:
            preference_range = None

    else:
        relevance_filter = binned_df["proportion"] >= relevance_threshold
        relevant_binned_df = binned_df[relevance_filter].copy()

        relevance_range = (relevant_binned_df["bin_value"].min(), relevant_binned_df["bin_value"].max())
        preference_range = None

    return relevance_range, preference_range, optimum


def prepare_and_check_dataframe (base_df, indicator):
    analysis_df = base_df[["species_total", indicator]].copy()
    no_null_filter = analysis_df["species_total"].notna() & analysis_df[indicator].notna()
    analysis_df = analysis_df[no_null_filter]

    if not check_low_deviation(analysis_df[indicator]):
        return analysis_df
    

def get_preference_dictionary (base_df, indicator, max_range, low_value_cap, high_value_cap):
    analysis_df = prepare_and_check_dataframe(base_df, indicator)

    if not isinstance(analysis_df, pd.DataFrame):
        return

    relevance_range, preference_range, optimum = calculate_ranges(analysis_df, indicator)

    relevance_range_abs = relevance_range[1] - relevance_range[0]

    preference_range_abs = (
        preference_range[1] - preference_range[0]
        if preference_range
        else None
    )

    if preference_range_abs:
        range_type = "narrow" if preference_range_abs / max_range < 0.25 else "wide"
    else:
        range_type = "narrow" if relevance_range_abs / max_range < 0.5 else "wide"

    optimum_type = (
        None if optimum is None
        else "low" if optimum < low_value_cap
        else "high" if optimum > high_value_cap
        else "medium"
    )

    return {
        "relevance_range": relevance_range,
        "preference_range": preference_range,
        "optimum": optimum,
        "range_type": range_type,
        "optimum_type": optimum_type
    }


    