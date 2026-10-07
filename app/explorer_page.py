import streamlit as st
import pandas as pd
from zipfile import ZipFile

from src.visualization.prepare_visualization import create_categorybased_visual
from src.analysis.variable_preparations import remove_variable_null_values
from app.streamlit_functions import explorer_button, lexicon_button, statistics_button

SPECIES_ZIP_PATH = "data/processed/species_csv_files.zip"

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


def get_explorer_content ():
    species_config = st.session_state["species_config"]

    # ==============================================================
    # Sidebar
    # ==============================================================
    
    with st.sidebar:
        with st.container(key="sidebar_navigation"):
            st.button(
                "Explorer", 
                disabled = st.session_state["page"] == "explorer", 
                width="stretch",
                on_click=explorer_button
            )
                
            st.button(
                "Lexicon", 
                disabled = st.session_state["page"] == "lexicon", 
                width="stretch",
                on_click=lexicon_button
            )

            st.button(
                "Statistics", 
                disabled = st.session_state["page"] == "statistics", 
                width="stretch",
                on_click=statistics_button
            )

        st.divider()
                    
        st.text_input("Species Search", key="species_search_input")

        species_list = st.session_state["species_list"]

        species_search = st.session_state.get("species_search_input", "")

        filtered_species_list = [
            species_tuple 
            for species_tuple in species_list 
            if species_search.lower() in species_tuple[1].lower()
        ]

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

    # ======================================================================================================
    # Main Content
    # ======================================================================================================

    species_dict = species_config[selected_species]
    audubon_info = species_dict["audubon_info"]
    common_name = audubon_info["common_name"]

    filename = f"{selected_species}.csv"

    with ZipFile(SPECIES_ZIP_PATH, "r") as zip:
        with zip.open(filename) as file:
            analysis_df = pd.read_csv(file, encoding="utf-8")
            st.session_state["analysis_frame"] = analysis_df

    analysis_df = remove_variable_null_values(analysis_df, selected_variable_indicator, "species_total")

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

    total_observation_count = analysis_df[selected_variable_indicator].size
    route_count = len(analysis_df["route_id"].unique())

    st.write(f"Total Observations: {total_observation_count}")
    st.write(f"Anzahl Routen: {route_count}")
