import math

def get_decimals(value):
    return max(1, math.ceil(-math.log10(value))) if value > 0 else 0

def build_range_string(caps):
    range = caps[1] - caps[0]

    decimals_range = get_decimals(range)

    decimals = map(lambda x: max(get_decimals(x), decimals_range), caps)
    caps_round = [round(cap, decimal) for cap, decimal in zip(caps, decimals)]

    return f"{caps_round[0]}-{caps_round[1]}"

def extract_bin_caps_from_label (label: str):
    if label[0] == "-":
        label = label[1:]

    label = label.replace("%", "")
    caps = list(map(lambda x: float(x.strip()), label.split("-")))

    return caps

def get_landcover_variable_range(label_list: list[str]):
    cleaned_list = [label for label in label_list if not (">" in label or "<" in label)]

    if len(cleaned_list) == 0:
        return 0, 0, 0 

    interval_list = list(map(extract_bin_caps_from_label, cleaned_list))

    lowest_cap = interval_list[0][0]
    highest_cap = interval_list[-1][1]

    return highest_cap - lowest_cap, lowest_cap, highest_cap    