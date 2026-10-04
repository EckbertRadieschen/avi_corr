import streamlit as st
from pathlib import Path
import base64

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = BASE_DIR / "assets"
LANDCOVER_ICONS_DIR = ASSETS_DIR / "landcover_icons"

LANDCOVER_VARIABLES = ["developed", "water", "forest", "barren", "shrubland", "grassland", "pasture", "cropland", "wetland"]

SPECIES_CONFIG_PATH = "src/config/species_config.json"
LANDCOVER_CONFIG_PATH = "src/config/landcover_config.json"

TREEMAP_NUMBER_MAP = {
    1: "first",
    2: "second",
    3: "third",
    4: "fourth",
    5: "fifth",
    6: "sixth",
    7: "seventh"
}

urbanization_tolerance_map = [
    (10),
    (15, "tolerant")
]

def water_visual(water_need):
    water_percent = round(water_need * 100)

    st.markdown(f"""
           <div class="water-gauge" style="--water: {water_percent}%;">
                <div class="water-fill">
                    <svg class="water-wave" viewBox="0 0 200 24"
                        preserveAspectRatio="none">
                        <path d="
                            M 0 12
                            C 25 0, 45 0, 70 10
                            S 115 22, 140 10
                            S 175 0, 200 10
                            L 200 24
                            L 0 24
                            Z
                        " />
                    </svg>
                </div>
                <div class="water-value">{water_percent}%</div>
            </div>
        """, unsafe_allow_html=True
    )


def urbanization_visual(urbanization_type, urbanization_range):
    st.markdown(f"""
        <div class="info-circle">
            <div class="info-content">
                {urbanization_type}<br>
                ({urbanization_range})
            </div>
        </div>  
    """, unsafe_allow_html=True
    )

    
def build_branch_html (landcover_list: list[dict], box_number=1, markdown_string=''):
    """Needs landcover_list to be ordered ascending by "proportion" """

    if len(landcover_list) == 0:
        return markdown_string

    landcover_dict = landcover_list.pop()

    variable = landcover_dict["variable"]
    proportion = landcover_dict["proportion"]
    box_measure = landcover_dict["measure"]
    box_background_hex = landcover_dict["background_hex"]
    box_image_path = LANDCOVER_ICONS_DIR / f"{variable}.png"
    
    if box_number % 2 == 1:
        box_height_str = remainder_height_str = "100%"
        
        box_width = box_measure
        box_width_str = f"{round(box_width * 100, 4)}%"
        
        remainder_width = 1 - box_width
        remainder_width_str = f"{round(remainder_width * 100, 4)}%"

        branch_type = "odd"
        
    else:
        box_width_str = remainder_width_str = "100%"
        
        box_height = box_measure
        box_height_str = f"{round(box_height * 100, 4)}%"
        
        remainder_height = 1 - box_height
        remainder_height_str = f"{round(remainder_height * 100, 4)}%"

        branch_type = "even"

    if box_image_path.is_file():
        encoded = base64.b64encode(
            box_image_path.read_bytes()
        ).decode("ascii")

    box_icon_html = (
        f'<img class="box-icon" '
        f'src="data:image/png;base64,{encoded}" '
        f'title="{variable.capitalize()}: {round(proportion * 100, 1)}%">'
    )
        
    branches_html = (
        f'<div class="{TREEMAP_NUMBER_MAP[box_number]}-box box"'
        f'style="width: {box_width_str}; height: {box_height_str}; background-color: {box_background_hex}">'
        f'{box_icon_html} </div>'
        f'<div class="{TREEMAP_NUMBER_MAP[box_number]}-remainder remainder {branch_type}" '
        f'style="width: {remainder_width_str}; height: {remainder_height_str}">'
    )

    markdown_string += branches_html

    box_number += 1

    return build_branch_html(landcover_list, box_number, markdown_string)


def setup_treemap_html (width, height, landcover_dict: dict):
    landcover_list = []

    total_remainder = 1
    for variable, variable_dict in landcover_dict.items():
        proportion = variable_dict["proportion"]

        landcover_list.append({
            "variable": variable,
            "proportion": proportion,
            "measure": proportion / total_remainder,
            "background_hex": variable_dict["background_hex"]
        })

        total_remainder -= proportion

    landcover_list = sorted(landcover_list, key=lambda x: x["proportion"])

    clothing_tags = '</div>' * len(landcover_list)

    branches_html = build_branch_html(landcover_list)

    treemap_html =  f"""
        <div class="treemap remainder even"
        style="
            width: {width}; 
            height: {height}
        ">
        {branches_html}
        {clothing_tags}
        </div>
    """

    return treemap_html


def get_preferred_habitat (landcover_preferences, landcover_config): 
    variable_tuples = []

    false_optimum = []
    preferred_variables = []

    landcover_dict = {}

    for variable in LANDCOVER_VARIABLES:
        variable_info = landcover_preferences[variable]
        mean = variable_info["preference_mean"]
        is_optimum = variable_info["is_real_optimum"]

        if not is_optimum:
            false_optimum.append(variable)

        variable_tuples.append((variable, mean))

    variable_tuples = sorted(variable_tuples, key=lambda x: x[1], reverse=True)

    treemap_tuples = [tuple for tuple in variable_tuples if not tuple[0] in ["water", "developed"]]
    treemap_total = sum(value for _, value in treemap_tuples) 

    for variable, value in treemap_tuples:
        variable_config = landcover_config[variable]

        normed_value = value / treemap_total

        if normed_value >= 1/3:
            preferred_variables.append(variable)

        landcover_dict[variable] = {
            "proportion": normed_value,
            "background_hex": variable_config["background_color"]
        }

    treemap_html = setup_treemap_html("100%", "280px", landcover_dict)

    st.markdown(
        treemap_html,
        unsafe_allow_html=True
    )



    

