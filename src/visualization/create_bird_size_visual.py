from pathlib import Path
import streamlit as st
import json

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = BASE_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "bird_size_icons"

SRC_DIR = BASE_DIR / "src"
CONFIG_DIR = SRC_DIR / "config"

SPECIES_CONFIG_PATH = CONFIG_DIR / "species_config.json"

SIZE_MAP = [
    (90, "xxl.png"),
    (60, "xl.png"),
    (40, "l.png"),
    (30, "m.png"),
    (20, "s.png"),
    (10, "xs.png"),
    (0, "xxs.png")
]


def create_bird_size_visual(measure_dict):
    if "female" in measure_dict:
        female_dict = measure_dict["female"]
        female_length_dict = female_dict["length"]
        male_dict = measure_dict["male"]
        male_length_dict = male_dict["length"]

        unit = female_length_dict["unit"]

        female_min = female_length_dict["lower"]
        female_max = female_length_dict["upper"]
        female_mean = (female_min + female_min) / 2
        female_string = f"{female_min:1f}-{female_max:1f}{unit}"

        male_min = male_length_dict["lower"]
        male_max = male_length_dict["upper"]
        male_mean = (male_min + male_max) / 2
        male_string = f"{male_min:1f}-{male_max:1f}{unit}"

        length_mean = (female_mean + male_mean) / 2

    else:
        length_dict = measure_dict["both_sexes"]["length"]
        
        unit = length_dict["unit"]
        length_min = length_dict["lower"]
        length_max = length_dict["upper"]
        length_mean = (length_min + length_max) / 2
        length_string = f"{length_min:1f}-{length_max:1f}{unit}"
    
    filename = next(name for value, name in SIZE_MAP if length_mean >= value)

    filepath = ICONS_DIR / filename

    st.write(filepath)
    
    # st.markdown(
    #     """
    #     <div class="visual_holder">
        
    #     </div>
    #     """, unsafe_allow_html=True
    # )