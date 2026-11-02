import streamlit as st
from pathlib import Path

from app.streamlit_functions import explorer_button, lexicon_button, statistics_button

from src.visualization.climate_bar_visualization import visualize_species_bars
from src.visualization.preferred_habitat_visual import get_preferred_habitat, water_visual, urbanization_visual
from src.visualization.create_bird_size_visual import create_bird_size_visual
from src.visualization.info_hover import create_info_hover_html

BASE_DIR = Path(__file__).resolve().parent.parent

SPECIES_MAP_VISUAL_DIR = BASE_DIR / "assets" / "map_visuals"

CONFIG_DIR = BASE_DIR / "src" / "config"
SPECIES_GRID_ZIP = CONFIG_DIR / "species_grid_configs.zip"


def get_lexicon_content():
    species_config = st.session_state["species_config"]
    hover_info_text_config = st.session_state["hover_info_text_config"]

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

        def reset_search_selection():
            st.session_state["selected_order"] = ("Any", "Any")
            st.session_state["selected_family"] = ("Any", "Any")
            st.session_state.pop("selected_species", None)
            st.session_state["selected_species"] = st.session_state["species_options"][0]

        selected_search_option = st.radio(
            "Search Options", 
            options=["Common Names", "Scientific Names"], 
            key="selected_search_option",
            on_change=reset_search_selection,
            width=300
        )

        def taxonomic_format (option, scientific_index, common_index):
            if selected_search_option == "Common Names":
                return option[common_index]
            else:
                return option[scientific_index]

        taxonomic_config = st.session_state["taxonomic_config"]
        taxonomic_orders = taxonomic_config["orders"]
        taxonomic_families = []

        for values in taxonomic_orders.values():
            for family, common_family in values["families"].items():
                taxonomic_families.append((family, common_family))

        all_orders = sorted(
            [
                (order, values["common_order"])
                for order, values in taxonomic_orders.items()
            ],
            key=lambda x: taxonomic_format(x, 0, 1)
        )

        order_list = [("Any", "Any")] + all_orders

        selected_order = st.selectbox(
            "Orders", 
            order_list, 
            format_func=lambda x: taxonomic_format(x, 0, 1),
            key="selected_order"
        )

        if selected_order[0] == "Any":
            all_families = taxonomic_families
        else:
            order_family_dict = taxonomic_orders[selected_order[0]]["families"]
            all_families = [
                (family, common_family) 
                for family, common_family in order_family_dict.items()
            ]

        all_families = sorted(all_families, key=lambda x: taxonomic_format(x, 0, 1))

        family_list = [("Any", "Any")] + all_families

        selected_family = st.selectbox(
            "Family", 
            family_list, 
            format_func=lambda x: taxonomic_format(x, 0, 1),
            key="selected_family"
        )

        all_species_list = st.session_state["species_list"]

        if selected_family[0] != "Any":
            species_list = [
                species
                for species in all_species_list
                if species[4] == selected_family[0]
            ]

        else:
            if selected_order[0] != "Any":
                species_list = [
                    species
                    for species in all_species_list
                    if species[3] == selected_order[0]
                ]

            else:
                species_list = st.session_state["species_options"] = all_species_list

        species_list = sorted(species_list, key=lambda x: taxonomic_format(x, 2, 1))

        st.selectbox(
            "Species", 
            species_list, 
            format_func=lambda x: taxonomic_format(x, 2, 1), 
            key="selected_species"
        )

        st.markdown(
            """
                <div class="sidebar_search_info">For Species Search type in selectbox above!</div>
            """,
            unsafe_allow_html=True
        )

        selected_species = st.session_state["selected_species"][0]
    
    # =======================================================================================================
    # Main Content
    # =======================================================================================================

    species_map_file_path = SPECIES_MAP_VISUAL_DIR / f"map_{selected_species}.png"

    species_dict = species_config[selected_species]
    audubon_info = species_dict["audubon_info"]
    population_estimated = audubon_info["Population"]
    iucn_status = audubon_info["IUCN Status"]

    common_name = audubon_info["common_name"]
    scientiftic_name = species_dict["scientific_name"]
    species_order = species_dict["order"]
    species_family = species_dict["family"]

    species_common_order = taxonomic_config["orders"][species_order]["common_order"]
    species_common_family = taxonomic_config["orders"][species_order]["families"][species_family]

    picture_content = audubon_info["picture"]
    
    picture_url = picture_content["url"]
    picture_author = picture_content["author"]

    measurements = audubon_info["measurements"]

    st.session_state["bird_gender"] = "male" if "male" in measurements else "both"

    with st.container(key="main_section"):

        col1, col2 = st.columns(2, gap=50)

        with col1:
            with st.container(key="map_container_holder", gap=5):
                st.subheader("Geographic Distribution", text_alignment="center")

                st.markdown(
                    create_info_hover_html(hover_info_text_config["geographic_distribution"]),
                    unsafe_allow_html=True
                )

                st.image(species_map_file_path)

                with st.container(key="map_info"):
                    with st.container(key="population_info"):
                        st.write(f"Population:")
                        st.write(population_estimated)
                    with st.container(key="iucn_status"):
                        st.write(f"IUCN Status:")
                        st.write(iucn_status)
            
            with st.container(key="bars_container", gap=5):
                st.subheader("Climate Preferences", text_alignment="center")

                st.markdown(
                    create_info_hover_html(hover_info_text_config["climate_preferences"]),
                    unsafe_allow_html=True
                )

                climate_preferences = species_dict["climate_preferences"]
                climate_config = st.session_state["climate_config"]

                visualize_species_bars(climate_config["variables"], climate_preferences)
            
        with col2:
            with st.container(key="infobox_container"):
                with st.container(key="info_header"):
                    st.header(common_name, text_alignment="center")
                    st.write(f"({scientiftic_name})")

                st.divider()
                
                with st.container(key="bird_info"):                
                    with st.container(key="bird_taxonomic"):
                        st.subheader("Taxonomic Information")

                        st.markdown(
                            f"""
                                <div class="taxonomic_information">
                                    <div class="taxonomic_titles">
                                        <span>Order:</span>
                                        <span>Family:</span>
                                    </div>
                                    <div class="taxonomic_values">
                                        <div class="tax_value_row">{species_order}<p>({species_common_order})</p></div>
                                        <div class="tax_value_row">{species_family}<p>({species_common_family})</p></div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True
                        )

                    with st.container(key="bird_picture"):
                        st.image(picture_url, caption=f"By: {picture_author}", width="stretch")

                with st.container(key="size_container"):
                    create_bird_size_visual(measurements)

            with st.container(key="habitat_container", width=600, height=373, gap=5):
                st.subheader("Habitat Preferences", text_alignment="center", )

                st.markdown(
                    create_info_hover_html(hover_info_text_config["habitat_preferences"]),
                    unsafe_allow_html=True
                )
                
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
                        st.markdown(
                            create_info_hover_html(hover_info_text_config["water_access"]),
                            unsafe_allow_html=True
                        )

                        water_visual(water_need)
                    with st.container(key="urbanization_visual"):
                        st.write("Urbanization Tolerance")
                        st.markdown(
                            create_info_hover_html(hover_info_text_config["urbanization_tolerance"]),
                            unsafe_allow_html=True
                        )

                        urbanization_visual(urbanization_type, urbanization_range)

        

      
        
        
            