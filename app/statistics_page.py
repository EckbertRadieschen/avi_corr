import streamlit as st
import pandas as pd

from app.streamlit_functions import (
    explorer_button, lexicon_button, statistics_button,
    top_button_main, bottom_button_main,
    top_button_width, bottom_button_width,
    top_button_urban, bottom_button_urban,
    top_button_water, bottom_button_water
)

from src.visualization.climate_stat_visualization import (
    main_bar_chart, range_type_pie, optimum_class_bars, range_width_chart
)

from src.visualization.landcover_stat_visualization import(
    habitat_type_bar_chart,
    urbanization_boxplot,
    water_urbanization_bar_chart
)

INDICATORS = {
    "temperature": [
        "mean_year", "mean_spring", "mean_summer", "mean_fall", "mean_winter",
        "min_year", "min_spring", "min_summer", "min_fall", "min_winter",
        "max_year", "max_spring", "max_summer", "max_fall", "max_winter",
        "std_year", "std_spring", "std_summer", "std_fall", "std_winter"
    ],
    "precipitation": ["sum_year", "sum_spring", "sum_summer", "sum_fall", "sum_winter", "max_month"],
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
}



def get_statistics_content ():
    with st.container(key="statistics_header", width="stretch"):
        with st.container(key="header_navigation", width="content"):
            st.button(
                "Explorer", 
                disabled = st.session_state["page"] == "explorer",  
                on_click=explorer_button
            )
                    
            st.button(
                "Lexicon", 
                disabled = st.session_state["page"] == "lexicon", 
                on_click=lexicon_button
            )

            st.button(
                "Statistics", 
                disabled = st.session_state["page"] == "statistics", 
                on_click=statistics_button
            )

        with st.container(key="header_slicer", width="content"):   
            climate_stat_config = st.session_state["climate_stat_config"]

            statistics_categories = ["Climate", "Landcover"]
            selected_stats_category = st.radio(
                "Statistics Category", 
                options=statistics_categories, 
                key="selected_stats_category",
                width=300
            )

            if selected_stats_category == "Climate":

                variable_list = [
                    (variable, variable.replace("_", " ").title())
                    for variable in INDICATORS.keys()
                ]   
                st.selectbox("Variable", variable_list, format_func= lambda x: x[1], key="selected_variable_header")
                selected_variable = st.session_state["selected_variable_header"][0]

                variable_config = climate_stat_config[selected_variable]
            
                species_values = variable_config["species_values"]
                meta_data = variable_config["meta_data"]
            
                min_value = meta_data["min"]
                max_value = meta_data["max"]
                slider_step = meta_data["slider_step"]
                unit = meta_data["unit"] if not selected_variable == "vegetation_coeff" else ""
                rounding_decimals = meta_data["rounding_decimals"]
                        
                min_chart, max_chart = st.slider(
                    "Optimum",
                    min_value=min_value,
                    max_value=max_value,
                    value=(min_value, max_value),
                    step=slider_step
                )

    # =======================================================================================================
    # Main Content
    # =======================================================================================================

    with st.container(key="main_section"):
        if st.session_state["selected_stats_category"] == "Climate":
            data = species_values.values()
            variable_df = pd.DataFrame(data)

            cap_filter = (variable_df["optimum"] <= max_chart) & (variable_df["optimum"] >= min_chart)
            variable_df = variable_df[cap_filter]

            sector_col1, sector_col2 = st.columns([3, 2], gap=50)

            with sector_col1:
                if not "top_bottom_main" in st.session_state:
                    st.session_state["top_bottom_main"] = "top"

                top_bottom_main = st.session_state["top_bottom_main"]

                with st.container(key="main_container", width="stretch", gap=0, border=True):
                    header_prefix_main = "Highest" if top_bottom_main == "top" else "Lowest"

                    with st.container(key="main_chart_header"):
                        st.subheader(
                            f"{header_prefix_main} by Preference {selected_variable.replace('_', ' ').title()}", 
                            width="stretch"
                        )

                        with st.container(key="top_bottom_button_container_main", width="stretch"):
                            st.button(
                                "Top", key="top_button_main", 
                                disabled=top_bottom_main == "top", width=100, on_click=top_button_main
                            )
                            st.button(
                                "Bottom", key="bottom_button_main",
                                disabled=top_bottom_main == "bottom", width=100, on_click=bottom_button_main
                            )

                    with st.container(key="main_chart_container", width="stretch"):
                        main_chart_fig = main_bar_chart(variable_df, top_bottom_main, rounding_decimals, unit)
                        st.plotly_chart(main_chart_fig, height=300, config={"displayModeBar": False})

                if not "top_bottom_width" in st.session_state:
                    st.session_state["top_bottom_width"] = "top"

                top_bottom_width = st.session_state["top_bottom_width"]

                with st.container(key="width_container", width="stretch", gap=0, border=True):
                    header_prefix_width = "Widest" if top_bottom_width == "top" else "Narrowest"

                    with st.container(key="width_chart_header"):
                        st.subheader(
                            f"{header_prefix_width} Preference Ranges by {selected_variable.replace('_', ' ').title()}", 
                            width="stretch"
                        )

                        with st.container(key="top_bottom_button_container_width", width="stretch"):
                            st.button(
                                "Top", key="top_button_width",
                                disabled=top_bottom_width == "top", width=100, on_click=top_button_width
                            )
                            st.button(
                                "Bottom", key="bottom_button_width",
                                disabled=top_bottom_width == "bottom", width=100, on_click=bottom_button_width
                            )

                    with st.container(key="width_chart_container", width="stretch"):
                        width_chart_fig = range_width_chart(variable_df, top_bottom_width, rounding_decimals, unit)
                        st.plotly_chart(width_chart_fig, height=300, config={"displayModeBar": False})

            with sector_col2:
                with st.container(key="optimum_bars_container", border=True):
                    optimum_class_fig = optimum_class_bars(selected_variable, variable_df)
                    st.plotly_chart(optimum_class_fig, height=335, width=550, config={"displayModeBar": False})

                with st.container(key="range_type_container", border=True):
                    range_type_fig = range_type_pie(selected_variable, variable_df)
                    st.plotly_chart(range_type_fig, height=335, width=500, config={"displayModeBar": False})

        # ===============================================================================================================
        # Landcover Statistics
        # ===============================================================================================================

        else:
            sector_col1, sector_col2 = st.columns(2, gap=50)

            landcover_type_data = st.session_state["landcover_type_data"]
            urbanization_tolerance_data = st.session_state["urbanization_tolerance_data"]
            water_access_data = st.session_state["water_access_data"]

            with sector_col1:
                with st.container(key="landcover_type_stats_container", border=True):
                    landcover_type_fig = habitat_type_bar_chart(landcover_type_data)
                    st.plotly_chart(landcover_type_fig, height=335, width=650, config={"displayModeBar": False})

                with st.container(key="urbanization_distribution_container", border=True):
                    urbanization_distribution_fig = urbanization_boxplot(urbanization_tolerance_data)
                    st.plotly_chart(urbanization_distribution_fig, height=335, width=600, config={"displayModeBar": False})

            with sector_col2:
                if not "top_bottom_water" in st.session_state:
                    st.session_state["top_bottom_water"] = "top"

                top_bottom_water = st.session_state["top_bottom_water"]

                with st.container(key="water_stats_container", width="stretch", gap=0, border=True):
                    header_prefix_water = "Highest" if top_bottom_water == "top" else "Lowest"

                    with st.container(key="water_stats_chart_header"):
                        st.subheader(
                            f"{header_prefix_water} by Water Access in Habitat", 
                            width="stretch"
                        )

                        with st.container(key="top_bottom_button_container_water", width="stretch"):
                            st.button(
                                "Top", key="top_button_water", 
                                disabled=top_bottom_water == "top", width=100, on_click=top_button_water
                            )
                            st.button(
                                "Bottom", key="bottom_button_water",
                                disabled=top_bottom_water == "bottom", width=100, on_click=bottom_button_water
                            )

                    with st.container(key="water_stats_chart_container", width="stretch"):
                        water_stats_chart_fig = water_urbanization_bar_chart(water_access_data, top_bottom_water)
                        st.plotly_chart(water_stats_chart_fig, height=300, config={"displayModeBar": False})

                if not "top_bottom_urban" in st.session_state:
                    st.session_state["top_bottom_urban"] = "top"

                top_bottom_urban = st.session_state["top_bottom_urban"]

                with st.container(key="urban_stats_container", width="stretch", gap=0, border=True):
                    header_prefix_urban = "Highest" if top_bottom_urban == "top" else "Lowest"

                    with st.container(key="urban_stats_chart_header"):
                        st.subheader(
                            f"{header_prefix_urban} Tolerance for Urbanization", 
                            width="stretch"
                        )

                        with st.container(key="top_bottom_button_container_urban", width="stretch"):
                            st.button(
                                "Top", key="top_button_urban",
                                disabled=top_bottom_urban == "top", width=100, on_click=top_button_urban
                            )
                            st.button(
                                "Bottom", key="bottom_button_urban",
                                disabled=top_bottom_urban == "bottom", width=100, on_click=bottom_button_urban
                            )

                    with st.container(key="urban_stats_chart_container", width="stretch"):
                        urban_chart_fig = water_urbanization_bar_chart(urbanization_tolerance_data, top_bottom_urban)
                        st.plotly_chart(urban_chart_fig, height=300, config={"displayModeBar": False})
                
            