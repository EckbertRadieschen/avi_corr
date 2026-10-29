import streamlit as st
import pandas as pd
from zipfile import ZipFile
from pathlib import Path

from src.analysis.models import get_model_info
from src.visualization.prepare_visualization import create_categorybased_visual
from src.analysis.variable_preparations import remove_variable_null_values
from app.streamlit_functions import explorer_button, lexicon_button, statistics_button

BASE_DIR = Path(__file__).resolve().parent.parent
SPECIES_ZIP_PATH = BASE_DIR / "data" / "processed" / "species_csv_files.zip"

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
    climate_config = st.session_state["climate_config"]

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
                    
        species_list = st.session_state["species_list"]

        st.selectbox("Species", species_list, format_func= lambda x: x[1], key="selected_species")
        selected_species = st.session_state["selected_species"][0]

        category_list = [
            (category, category.replace("_", " ").title()) 
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

    if selected_category == "climate":
        indicator_dict = climate_config["variables"][selected_variable][selected_variable_indicator]
        indicator_unit = indicator_dict["unit"] if indicator_dict["unit"] is not None else "units"
        round_decimals = indicator_dict["round_decimals"]

    if selected_category == "land_cover":
        indicator_unit = "%"
        round_decimals = 1

    with st.container(key="main_section", width="stretch"):

        st.title("Data Explorer")

        figure, model, model_type, error_message = create_categorybased_visual(
            selected_category, 
            analysis_df, 
            selected_variable_indicator, 
            indicator_unit,
            round_decimals
        )

        with st.container(key="main_explorer_container", border=True):

            if error_message:
                st.write(error_message)
                st.stop()

            st.plotly_chart(
                figure, 
                config={"displayModeBar": False}
            )

        with st.container(key="explorer_infobox_headers"):
            if selected_category == "climate":
                st.subheader("Info: Used Model")
            if selected_category == "land_cover":
                st.subheader("Info: Bar Extension Method")
            
            st.subheader("Info: Used Data")

        with st.container(key="explorer_info_boxes"):
            if selected_category == "climate":
                with st.container(key="explorer_model_info", border=True):
                    model_info = get_model_info(model, model_type)

                    with st.container(key="model_info_titles"):
                        for title in model_info:
                            st.write(title)
                        
                    with st.container(key="model_info_values"):
                        for value in model_info.values():
                            st.write(str(value))

            if selected_category == "land_cover":
                with st.container(key="landcover_binning_info", border=True):
                    st.write("If border bins (high and/or low) are strongly populated")
                    st.write("there is a additional binning of these value ranges.")
                    st.write("Regular bins are marked orange.")
                    st.write("Additional bins are marked red.")
                    
            total_observation_count = analysis_df[selected_variable_indicator].size
            route_count = len(analysis_df["route_id"].unique())
            max_year = analysis_df["year"].max()
            min_year = analysis_df["year"].min()
            year_count = len(analysis_df["year"].unique())
        
            with st.container(key="explorer_data_info", border=True):
                with st.container(key="data_info_titles"):
                    st.write("Species")
                    st.write("Observation Years")
                    st.write("Route Count")
                    st.write("Total Observations")

                with st.container(key="data_info_values"):
                    st.write(common_name)
                    st.write(f"{min_year}-{max_year} (Total: {year_count})")
                    st.write(str(route_count))
                    st.write(str(total_observation_count))

            

            
