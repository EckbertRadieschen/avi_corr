import streamlit as st

def apply_markdown():
    st.markdown(
        """
            <style>
            
            /* ==========================================================
            === Sidebar
            ========================================================== */

            .st-key-sidebar_title_container {
                background-color: #c93e20;
                width: 100%;
                margin-bottom: 1.5rem;
                border-radius: 0
            }

            section[data-testid="stSidebar"] {
                border-right: 1px solid;
                border-color: #a67b5b;
                padding: 2rem 1rem
            }

            [data-testid="stSidebarContent"] {
                padding: 0 10px
            }

            .st-key-sidebar_navigation {
                display: flex;
                margin-bottom: 1rem
            }

            [data-testid="stButton"] > button {
                background-color: #e8c158;
                color: #ffffff;
                height: fit-content;
                min-height: 1rem
            }

            [data-testid="stButton"] > button:hover {
                background-color: #f9d269;
                color: #ffffff
            }

            [data-testid="stButton"] > button:disabled {
                background-color: #bfa26b;
                color: #dddddd
            }

            [data-testid="stButton"] > button:disabled:hover {
                background-color: #bfa26b;
                color: #dddddd
            }

            [data-testid="stButton"] > button p {
                font-size: 16px;
            }

            [data-testid="stSidebarContent"] > div {
                padding: 0 !important;
                margin: 0 !important;
            }

            [data-testid="stWidgetLabel"] p {
                font-size: 16px;
                color: #ffffff
            }

            [data-testid="stSidebarHeader"] {
                display: none !important
            }

            /* Divider */
            div[data-testid="stMarkdown"] hr {
                margin-top: 0.25rem;
                margin-bottom: 20px
            }

            /* Selectbox Container 
            div[data-testid="stSelectbox"] div.react-aria-ComboBox > div {
                min-height: 25px;
                height: 25px
            }*/

            /* Text in der Selectbox 
            div[data-testid="stSelectbox"] input {
                font-size: 0.65rem
            }*/

            /* Dropdown-Pfeil 
            div[data-testid="stSelectbox"] button svg {
                height: 1rem;
                width: 1rem
            } */

            /* Dropdown */
            div[role="listbox"] {
                max-height: 320px !important;
                font-size: 1rem;
                padding-top: 15px !important
            }

            /* Einträge im Dropdown */
            div[role="option"] {
                font-size: 0.8rem;
                height: 10px !important;
                padding-left: 0.5rem;
                padding-right: 0.5rem;
                margin-bottom: 0;
            }

            /* ==========================================================
            === Hauptbereich Header
            ========================================================== */

            header[data-testid="stHeader"] {
               display: None
            }

            [data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] {
                gap: 0
            }

            [data-testid="stMainBlockContainer"] {
                padding: 0
            }

            .st-key-statistics_header {
                display: flex;
                flex-flow: row nowrap;
                justify-content: space-between;
                background-color: #f2dcb8;
                padding: 10px 10px;
                align-items: center
            }

            .st-key-header_navigation{
                display: flex;
                flex-flow: row nowrap;
                margin-left: 30px
            }

            .st-key-header_slicer {
                display: flex;
                flex-flow: row nowrap;
                margin-bottom: 10px;
                padding-right: 10px;
                gap: 50px
            }

            .st-key-header_slicer * {
                color: #333
            }

            .st-key-header_slicer [data-testid="stWidgetLabel"] * {
                color: #333;
            }

            .st-key-selected_variable_header {
                width: 30%
            }

            
            /* ==========================================================
            === Hauptbereich
            ========================================================== */    

            .st-key-main_section p {
                margin: 0
            }

            .st-key-main_section {
                width: 100%;
                padding: 10px 100px 50px 100px
            }

            h3 span {
                font-size: 22px
            }

            .stHeading {
                display: flex;
                align-items: center
            }

            [data-testid="stHeaderActionElements"] {
                display: none
            }

            .st-key-map_container_holder {
                height: 300px;
                display: flex;
                align-items: center;
                border-radius: 25px;
                border: 1px solid #880000;
                padding: 20px 40px;
                margin-top: 10px
            }

            [data-testid="stLayoutWrapper"]:has(.st-key-map_container_holder) {
                height: 420px        
            }

            .st-key-map_container_holder h3{
                padding-top: 0;
                margin-top: -5px
            }

            .st-key-map_container {
                width: 100%;
                border-radius: 25px;
                border: 1px solid #880000;
                overflow: hidden;
                margin: 20px 0 30px 0
            }

            .map-loading-placeholder {
                width: 100%;
                height: 280px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px
            }

            .st-key-map_container .maplibregl-ctrl-bottom-right {
                display: none !important
            }

            .st-key-bars_container {
                border-radius: 25px;
                border: 1px solid #880000;
                padding: 40px 60px 40px 60px
            }

            .st-key-bars_container h3 {
                padding-top: 0;
                padding-bottom: 20px;
                margin-top: -8px
            }

            .st-key-infobox_container {
                border-radius: 25px;
                border: 1px solid #880000;
                padding: 20px 20px;
                margin-top: 10px 
            }

            .st-key-info_header h2{
                padding: 0
            }

            .st-key-info_header h2 span{
                font-size: 28px
            }

            .st-key-infobox_container h3 span{
                font-size: 18px
            }

            .st-key-bird_info {
                display: flex;
                flex-flow: row nowrap;
                padding: 0 5px 5px 5px
            }

            [data-testid="stLayoutWrapper"]:has(>.st-key-bird_picture) {
                width: 40%
            }

            [data-testid="stLayoutWrapper"]:has(>.st-key-bird_taxonomic) {
                width: 60%
            }

            .st-key-info_header p{
                text-align: center;
                font-style: italic
            }

            .st-key-infobox_container div[data-testid="stImage"] {
                height: 80%;
                width: 100%; 
                margin-top: 15px
            }

            .st-key-infobox_container [data-testid="stElementToolbar"] {
                display: none;
            }

            .st-key-habitat_container {
                border-radius: 25px;
                border: 1px solid #880000;
                padding: 0 10px
            }

            .st-key-habitat_container h3 {
                padding-top: 8px;
                padding-bottom: 20px
            }

            .st-key-water_visual,
            .st-key-urbanization_visual {
                width: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 3px;
                margin-bottom: 20px
            }

            .st-key-water_visual [data-testid="stElementContainer"],
            .st-key-urbanization_visual [data-testid="stElementContainer"] {
                width: 100%;
                display: flex;
                justify-content: center
            }

            .st-key-water_visual p,
            .st-key-urbanization_visual p {
                font-size: 1rem;
                font-weight: bold;
                text-align: center;
                margin-bottom: 20px !important
            }

            .st-key-size_container {
                position: relative;
                width: 100%;
                border-radius: 25px;
                border: 1px solid #880000;
                min-height: 185px !important;
                padding: 0 30px 0px 35px
            }

            .st-key-main_container, .st-key-width_container {
                padding-top: 20px
            }

            .st-key-main_chart_header, .st-key-width_chart_header {
                display: flex;
                flex-direction: row;
                justify-content: center
            }

            .st-key-main_chart_header > [data-testid="stElementContainer"], .st-key-width_chart_header > [data-testid="stElementContainer"]{
                display: flex;
                flex-flow: row nowrap;
                justify-content: center;
                align-items: center
            }

            .st-key-main_chart_header h3, .st-key-width_chart_header h3 {
                text-align: center;
                padding: 0
            }

            .st-key-main_chart_header h3 span, .st-key-width_chart_header h3 span {
                font-size: 20px;
                font-weight: bold
            }

            .st-key-main_chart_header > [data-testid="stElementContainer"]:has([data-testid="stHeading"]) {
                flex: 3 
            }

            [data-testid="stLayoutWrapper"]:has(>.st-key-top_bottom_button_container_main) {
                flex: 1
            }

            .st-key-width_chart_header > [data-testid="stElementContainer"]:has([data-testid="stHeading"]) {
                flex: 3 
            }

            [data-testid="stLayoutWrapper"]:has(>.st-key-top_bottom_button_container_width) {
                flex: 1
            }

            .st-key-top_bottom_button_container_main, .st-key-top_bottom_button_container_width {
                display: flex;
                flex-direction: row
            }

            .st-key-main_section [data-testid="stButton"] > button p {
                font-size: 14px !important;
            }

            .st-key-main_section [data-testid="stButton"] > button {
                padding: 3px 5px
            }

            .st-key-optimum_bars_container, .st-key-range_type_container {
                display: flex;
                align-items: center
            }


            </style>
        """, unsafe_allow_html=True
    )