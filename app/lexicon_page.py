import streamlit as st

from app.streamlit_functions import explorer_button, lexicon_button, statistics_button

from src.visualization.climate_bar_visualization import visualize_species_bars
from src.visualization.preferred_habitat_visual import get_preferred_habitat, water_visual, urbanization_visual
from src.visualization.create_concentration_map import plot_species_usa_map
from src.visualization.create_bird_size_visual import create_bird_size_visual


def get_lexicon_content():
    species_config = st.session_state["species_config"]

    # =======================================================================================================
    # Sidebar
    # =======================================================================================================

    with st.sidebar:
        with st.container(key="sidebar_navigation"):
            st.button(
                "Explorer", 
                disabled = st.session_state["page"] == "explorer", 
                use_container_width=True, 
                on_click=explorer_button
            )
                
            st.button(
                "Lexicon", 
                disabled = st.session_state["page"] == "lexicon", 
                use_container_width=True, 
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
    
    # =======================================================================================================
    # Main Content
    # =======================================================================================================

    species_dict = species_config[selected_species]
    audubon_info = species_dict["audubon_info"]

    common_name = audubon_info["common_name"]
    scientiftic_name = species_dict["scientific_name"]
    order = species_dict["order"]
    family = species_dict["family"]
    genus = species_dict["genus"]
    
    picture_url = audubon_info["picture"]["url"]

    measurements = audubon_info["measurements"]

    col1, col2 = st.columns(2, gap=50)

    with col1:
        with st.container(key="map_container_holder"):
            st.subheader("Geographic Distribution", text_alignment="center")

            with st.container(key="map_container"):
                grid_config = st.session_state["grid_config"]

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
            st.subheader("Climate Preferences", text_alignment="center")

            climate_preferences = species_dict["climate_preferences"]
            climate_config = st.session_state["climate_config"]

            visualize_species_bars(climate_config["variables"], climate_preferences)
        
    with col2:
        with st.container(key="infobox_container"):
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

            with st.container(key="size_container"):
                create_bird_size_visual(measurements)


        with st.container(key="habitat_container", width=600, height=360, gap=5):
            st.subheader("Habitat Preferences", text_alignment="center", )
            
            habitat_col1, habitat_col2= st.columns([6, 2])

            with habitat_col1:
                landcover_preferences = species_dict["landcover_preferences"]
                landcover_config = st.session_state["landcover_config"]

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

    