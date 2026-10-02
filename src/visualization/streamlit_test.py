import os
from dotenv import load_dotenv

from zipfile import ZipFile

import pandas as pd
import numpy as np
import streamlit as st
from sqlalchemy.engine import URL
from sqlalchemy import create_engine
import json

from analysis.variable_preparations import remove_variable_null_values
from visualization.prepare_visualization import create_categorybased_visual
from visualization.create_climate_bars import climate_bar
from visualization.css import climate_bar_css, treemap_css, water_need_css, urbanization_css
from visualization.markdown import apply_markdown   

from visualization.streamlit_functions import explorer_button, lexicon_button
from visualization.climate_bar_visualization import visualize_species_bars
from visualization.preferred_habitat_visual import get_preferred_habitat, water_visual, urbanization_visual
from visualization.create_concentration_map import plot_species_usa_map
from visualization.create_bird_size_visual import create_bird_size_visual


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

SPECIES_ZIP_PATH = "data/processed/species_csv_files.zip"
SPECIES_CONFIG_PATH = "src/config/species_config.json"
ROUTE_CONFIG_PATH = "src/config/route_config.json"
GRID_CONFIG_PATH = "src/config/grid_config.json"
DISPLAY_GRID_CONFIG_PATH = "src/config/display_grid_config.json"

CLIMATE_CONFIG_PATH = "src/config/climate_config.json"
LANDCOVER_CONFIG_PATH = "src/config/landcover_config.json"

INDICATORS = {
    "climate": {
        "temperature": [
            "mean_year", "mean_spring", "mean_summer", "mean_fall", "mean_winter",
            "min_year", "min_spring", "min_summer", "min_fall", "min_winter",
            "max_year", "max_spring", "max_summer", "max_fall", "max_winter",
            "std_year", "std_spring", "std_summer", "std_fall", "std_winter"
        ],
        "precipitation": ["sum_year", "sum_spring", "sum_summer", "sum_fall", "sum_winter", "max_month"],
        "snowfall": ["sum_year", "sum_spring", "sum_summer", "sum_fall", "sum_winter", "max_month"],
        "wind_magnitude": ["mean_year", "mean_spring", "mean_summer", "mean_fall", "mean_winter", "max_year"],
        "relative_humidity": [
            "mean_year", "mean_spring", "mean_summer", "mean_fall", "mean_winter",
            "min_year", "min_spring", "min_summer", "min_fall", "min_winter",
            "max_year", "max_spring", "max_summer", "max_fall", "max_winter",
            "std_year", "std_spring", "std_summer", "std_fall", "std_winter"
        ],
        "soil_moisture": [
            "mean_year", "mean_spring", "mean_summer", "mean_fall", "mean_winter",
            "min_year", "min_spring", "min_summer", "min_fall", "min_winter",
            "max_year", "max_spring", "max_summer", "max_fall", "max_winter",
            "std_year", "std_spring", "std_summer", "std_fall", "std_winter"
        ],
        "solar_flux_density": ["mean_year", "mean_spring", "mean_summer", "mean_fall", "mean_winter"],
        "vegetation_coeff": ["mean_year", "mean_spring", "mean_summer", "mean_fall", "mean_winter"]
    },
    "land_cover": {
        "water": [None],
        "developed": [None],
        "barren": [None],
        "forest": [None],
        "shrubland": [None],
        "grassland": [None],
        "pasture": [None],
        "cropland": [None],
        "wetland": [None]
    }
}

# =====================================================

def print_value_list (column: pd.Series):
    meine_liste = column.sort_values().unique()
    print(*meine_liste, sep="\n")

# ============================================================================================================
# App
# ============================================================================================================


# =================================================================
# CSS

apply_markdown()
climate_bar_css()
treemap_css()
water_need_css()
urbanization_css()


st.set_page_config(layout="wide")

if "page" not in st.session_state:
    st.session_state["page"] = "explorer"

if "species_config" not in st.session_state:
    with open(SPECIES_CONFIG_PATH, "r") as file:
        st.session_state["species_config"] = json.load(file)

species_config = st.session_state["species_config"]

if "route_config" not in st.session_state:
    with open(ROUTE_CONFIG_PATH, "r") as file:
        st.session_state["route_config"] = json.load(file)

route_config = st.session_state["route_config"]

if "grid_config" not in st.session_state:
    with open(DISPLAY_GRID_CONFIG_PATH, "r") as file:
        st.session_state["grid_config"] = json.load(file)

grid_config = st.session_state["grid_config"]

if "climate_config" not in st.session_state:
    with open(CLIMATE_CONFIG_PATH, "r") as file:
        st.session_state["climate_config"] = json.load(file)

climate_config = st.session_state["climate_config"]

if "landcover_config" not in st.session_state:
    with open(LANDCOVER_CONFIG_PATH, "r") as file:
        st.session_state["landcover_config"] = json.load(file)

landcover_config = st.session_state["landcover_config"]

if "species_list" not in st.session_state:
    species_list = []

    for species_id, species_dict in species_config.items():
        audubon_info = species_dict["audubon_info"]
        meta_data = species_dict["meta_data"]
        common_name = audubon_info["common_name"]

        if meta_data["total_observations"] >= 250:
            species_list.append((species_id, common_name))

    # st.session_state["species_list"] = species_list
    st.session_state["species_list"] = sorted(species_list, key=lambda x: x[1])

species_list = st.session_state["species_list"]

species_search = st.session_state.get("species_search_input", "")

filtered_species_list = [
    species_tuple 
    for species_tuple in species_list 
    if species_search.lower() in species_tuple[1].lower()
]


# ==============================================================
# Sidebar
# ==============================================================

with st.sidebar:

    with st.container(key="sidebar_navigation"):
        nav_button_cols = st.columns(2)

        with nav_button_cols[0]:
            st.button(
                "Explorer", 
                disabled = st.session_state["page"] == "explorer", 
                use_container_width=True, 
                on_click=explorer_button
            )
                
        with nav_button_cols[1]:
            st.button(
                "Lexicon", 
                disabled = st.session_state["page"] == "lexicon", 
                use_container_width=True, 
                on_click=lexicon_button
            )
            

    st.text_input("Species Search", key="species_search_input")

    st.selectbox("Species", filtered_species_list, format_func= lambda x: x[1], key="selected_species")
    selected_species = st.session_state["selected_species"][0]

    category_list = [
        (category, category.replace("_", " ").capitalize()) 
        for category in INDICATORS.keys()
    ]
    st.selectbox("Category", category_list, format_func= lambda x: x[1], key="selected_category")
    selected_category = st.session_state["selected_category"][0]

    variable_dict = INDICATORS[selected_category]
    variable_list = [
        (variable, variable.replace("_", " ").capitalize())
        for variable in variable_dict.keys()
    ]   
    st.selectbox("Variable", variable_list, format_func= lambda x: x[1], key="selected_variable")
    selected_variable = st.session_state["selected_variable"][0]
    

    indicator_method_list = [
        (method, method.replace("_", " ").capitalize())
        if method is not None
        else (None, "Proportion")
        for method in variable_dict[selected_variable]
    ]
    st.selectbox("Indicator Method", indicator_method_list, format_func= lambda x: x[1], key="selected_indicator_method")
    selected_indicator_method = st.session_state["selected_indicator_method"][0]
    
selected_variable_indicator = (
    f"{selected_variable}_{selected_indicator_method}" 
    if selected_indicator_method is not None 
    else selected_variable
)


# =======================================================================================================
# Main Content
# =======================================================================================================

species_dict = species_config[selected_species]
audubon_info = species_dict["audubon_info"]
common_name = audubon_info["common_name"]


filename = f"{selected_species}.csv"

with ZipFile(SPECIES_ZIP_PATH, "r") as zip:
    with zip.open(filename) as file:
        analysis_df = pd.read_csv(file, encoding="utf-8")
        st.session_state["analysis_frame"] = analysis_df

total_observation_count = analysis_df[selected_variable_indicator].size
route_count = len(analysis_df["route_id"].unique())

analysis_df = remove_variable_null_values(analysis_df, selected_variable_indicator, "species_total")


if st.session_state["page"] == "lexicon":
    scientiftic_name = species_dict["scientific_name"]
    order = species_dict["order"]
    family = species_dict["family"]
    genus = species_dict["genus"]
    
    picture_url = audubon_info["picture"]["url"]
    habitat = audubon_info["Habitat"]

    measurements = audubon_info["measurements"]
        

    # length_dict = measurements["length"]
    # bird_length = f"{length_dict['lower']}-{length_dict['upper']} {length_dict['unit']}"

    # span_dict = measurements["wingspan"]
    # bird_span = f"{span_dict['lower']}-{span_dict['upper']} {span_dict['unit']}"

    # weight_dict = measurements["weight"]
    # bird_weight = f"{weight_dict['lower']}-{weight_dict['upper']} {weight_dict['unit']}"    


    col1, col2 = st.columns(2, gap=50)

    with col1:
        with st.container(key="map_container_holder"):
            st.subheader("Geographic Distribution", text_alignment="center")

            with st.container(key="map_container"):
                fig_map = plot_species_usa_map(grid_config, selected_species)
                st.plotly_chart(
                    fig_map, 
                    width="stretch", 
                    config={
                        "displayModeBar": False,
                        "scrollZoom": True,
                        "doubleClick": False,
                        "showTips": False
                    })

        with st.container(key="bars_container", gap=5):
            st.subheader("Climate Preferences", text_alignment="center", )

            climate_preferences = species_dict["climate_preferences"]
            visualize_species_bars(climate_config["variables"], climate_preferences)
        
    with col2:
        with st.container(key="infobox_container"):
            create_bird_size_visual(measurements)

            with st.container(key="info_header"):
                st.header(common_name, text_alignment="center")
                st.write(f"({scientiftic_name})")

            st.divider()
           
            _, info_col1, info_col2, _ = st.columns([1, 8, 9, 1], gap=20)

            with info_col1:
                st.subheader("Taxonomic Information:")
                st.write(f"Order: {order}")
                st.write(f"Family: {family}")
                st.write(f"Genus: {genus}")

            with info_col2:
                st.image(picture_url, width="stretch")
            
            # st.write(f"Length:   {bird_length}")
            # st.write(f"Wingspan: {bird_span}")
            # st.write(f"Weight:   {bird_weight}")


        with st.container(key="habitat_container", width=600, height=360, gap=5):
            st.subheader("Habitat Preferences", text_alignment="center", )
            
            habitat_col1, habitat_col2= st.columns([6, 2])

            with habitat_col1:
                landcover_preferences = species_dict["landcover_preferences"]
                get_preferred_habitat(landcover_preferences, landcover_config)

            with habitat_col2:
                water_need = landcover_preferences["water"]["water_need"]
                urbanization_type = landcover_preferences["developed"]["urbanization_type"]
                urbanization_range = landcover_preferences["developed"]["urbanization_range"]

                with st.container(key="water_visual"):
                    st.write("Water Access")
                    water_visual(water_need)
                with st.container(key="urbanization_visual"):
                    st.write("Urbanization Tolerance")
                    urbanization_visual(urbanization_type, urbanization_range)


            

elif st.session_state["page"] == "explorer":
    figure = create_categorybased_visual(selected_category, analysis_df, selected_variable_indicator)

    if isinstance(figure, str):
        info_message = figure
        st.write(info_message)
        st.stop()

    if isinstance(figure, tuple):
        figure, info_text = figure

    else:
        info_text = None

    _ , title_col, _ = st.columns([2, 5, 2])

    with title_col:
        st.title(common_name)

    st.plotly_chart(
        figure, 
        config={"displayModeBar": False}
    )

    if info_text:
        st.write(info_text)

    st.write(f"Total Observations: {total_observation_count}")
    st.write(f"Anzahl Routen: {route_count}")


