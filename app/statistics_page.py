import streamlit as st

from app.streamlit_functions import explorer_button, lexicon_button


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
    # =======================================================================================================
    # Sidebar
    # =======================================================================================================

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
                    
            variable_list = [
                (variable, variable.replace("_", " ").capitalize())
                for variable in INDICATORS.keys()
            ]   
            st.selectbox("Variable", variable_list, format_func= lambda x: x[1], key="selected_variable")
            selected_variable = st.session_state["selected_variable"][0]
            
            indicator_method_list = [
                (method, method.replace("_", " ").capitalize())
                if method is not None
                else (None, "Proportion")
                for method in INDICATORS[selected_variable]
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

    climate_stat_config = st.session_state["climate_stat_config"]

    