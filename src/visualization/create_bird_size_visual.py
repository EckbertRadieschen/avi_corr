from pathlib import Path
import streamlit as st
import base64
from app.streamlit_functions import male_button, female_button
from app.css import bird_size_css

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

    return f"{lower:.1f} - {upper:.1f} {unit}"


def create_bird_size_visual(measure_dict):
    bird_size_css()

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

        if st.session_state.get("bird_gender", "Male") == "Male":
            length = extract_info_string(male_dict["length"])
            span = extract_info_string(male_dict["wingspan"])
            weight = extract_info_string(male_dict["weight"])

        else:
            length = extract_info_string(female_dict["length"])
            span = extract_info_string(female_dict["wingspan"])
            weight = extract_info_string(female_dict["weight"])

    else:
        main_dict = measure_dict["both_sexes"]
        length_dict = main_dict["length"]
        
        length_min = length_dict["lower"]
        length_max = length_dict["upper"]
        length_mean = (length_min + length_max) / 2

        length = extract_info_string(main_dict["length"])
        span = extract_info_string(main_dict["wingspan"])
        weight = extract_info_string(main_dict["weight"])

    with st.container(key="measurments_box", gap=0):
        with st.container(key="measurements_header"):
            st.subheader("Measurements")
            st.button(
                "♂", 
                key="male_button", 
                disabled=st.session_state["bird_gender"] == "male", 
                on_click=male_button
            )
            st.button(
                "♀", 
                key="female_button",
                disabled=st.session_state["bird_gender"] == "female", 
                on_click=female_button
            )

        st.markdown(
            f"""
            <div class="measurements">
                <div class="measure_title">
                    <span>Length:</span>
                    <span>Wingspan:</span>
                    <span>Weight:</span>
                </div>
                <div class="measure_value">
                    <p>{length}</p>
                    <p>{span}</p>
                    <p>{weight}</p>
                </div>
            </div>
            """, unsafe_allow_html=True
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
            {size_html}
        </div>
        """, unsafe_allow_html=True
    )

    