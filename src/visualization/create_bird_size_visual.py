from pathlib import Path
import streamlit as st
import base64

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = BASE_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "bird_size_icons"

SRC_DIR = BASE_DIR / "src"
CONFIG_DIR = SRC_DIR / "config"

SPECIES_CONFIG_PATH = CONFIG_DIR / "species_config.json"

SIZE_MAP = [
    (90, "xxl"),
    (60, "xl"),
    (40, "l"),
    (30, "m"),
    (20, "s"),
    (10, "xs"),
    (0, "xxs")
]

def extract_info_string (dict):
    lower = dict["lower"]
    upper = dict["upper"]
    unit = dict["unit"]

    return f"{lower:.1f}-{upper:.1f}{unit}"


def create_bird_size_visual(measure_dict):
    if "female" in measure_dict:
        female_dict = measure_dict["female"]
        female_length_dict = female_dict["length"]
        male_dict = measure_dict["male"]
        male_length_dict = male_dict["length"]

        female_min = female_length_dict["lower"]
        female_max = female_length_dict["upper"]
        female_mean = (female_min + female_max) / 2

        male_min = male_length_dict["lower"]
        male_max = male_length_dict["upper"]
        male_mean = (male_min + male_max) / 2
        
        length_mean = (female_mean + male_mean) / 2

        length_1 = extract_info_string(male_dict["length"])
        length_2 = extract_info_string(female_dict["length"])
        span_1 = extract_info_string(male_dict["wingspan"])
        span_2 = extract_info_string(female_dict["wingspan"])
        weight_1 = extract_info_string(male_dict["weight"])
        weight_2 = extract_info_string(female_dict["weight"])

        size_info_html = (
            '<div class="measurements">'
                '<div class="measurements-header">'
                    '<div></div>'
                    '<div>♂</div>'
                    '<div>♀</div>'
                '</div>'
                '<div class="measurements-row">'
                    '<div>Length:</div>'
                    f'<div>{length_1}</div>'
                    f'<div>{length_2}</div>'
                '</div>'
                '<div class="measurements-row">'
                    '<div>Wing-span:</div>'
                    f'<div>{span_1}</div>'
                    f'<div">{span_2}</div>'
                '</div>'
                '<div class="measurements-row">'
                '<div>Weight:</div>'
                    f'<div">{weight_1}</div>'
                    f'<div>{weight_2}</div>'
                '</div>'
            '</div>'
        )

    else:
        main_dict = measure_dict["both_sexes"]
        length_dict = main_dict["length"]
        
        length_min = length_dict["lower"]
        length_max = length_dict["upper"]
        length_mean = (length_min + length_max) / 2

        length_string = extract_info_string(main_dict["length"])
        span_string = extract_info_string(main_dict["wingspan"])
        weight_string = extract_info_string(main_dict["weight"])

        size_info_html = (
            '<div class="measurements-single">'
                '<div></div>'
                '<div>Measurements</div>'
                '<div>Length:</div>'
                f'<div>{length_string}</div>'
                '<div>Wing-span:</div>'
                f'<div>{span_string}</div>'
                '<div>Weight:</div>'
                f'<div>{weight_string}</div>'
            '</div>'
        )
        
    species_size = next(name for value, name in SIZE_MAP if length_mean >= value)

    size_html = ''

    size_list = ["xxs", "xs", "s", "m", "l", "xl", "xxl"]
    base_width = 23
    step = 10
    size_tuple_list = []

    for n, size in enumerate(size_list):
        step_factor = 0
        
        for i in range(0, n + 1):
            step_factor += 0.5 * i

        size_tuple_list.append((size, f"{base_width + step * step_factor}px"))

    for compare_size, width in size_tuple_list:
        opacity = 1 if compare_size == species_size else 0.3
        height = width

        style = f'opacity: {opacity}; width: {width}; height: {height}'

        image_path = ICONS_DIR / f"{compare_size}.png"

        encoded = base64.b64encode(
            image_path.read_bytes()
        ).decode("ascii")

        size_html += (
            '<div class="image-holder">'
            f'<img class="box-icon" '
            f'src="data:image/png;base64,{encoded}" ' 
            f'style="{style}">'
            '</div>'
        )
    
    st.markdown(
        f"""
        <div class="visual_holder">
            {size_info_html}
            {size_html}
        </div>
        """, unsafe_allow_html=True
    )