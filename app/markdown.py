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
                margin-bottom: 1rem
            }

            [data-testid="stButton"] > button {
                background-color: #e8c158;
                color: #ffffff
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

            .block-container {
                padding-top: 0.5rem;
            }

            [data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] {
                gap: 0.4rem;
            }

            /* ==========================================================
            === Hauptbereich
            ========================================================== */    

            h3 span {
                font-size: 22px
            }

            [data-testid="stHeaderActionElements"] {
                display: none;
            }

            .st-key-map_container_holder {
                height: 300px;
                display: flex;
                align-items: center;
                border-radius: 25px;
                border: 1px solid #880000;
                padding: 20px 40px          
            }

            .st-key-map_container_holder h3{
                padding-top: 0;
                margin-top: -5px
            }

            .st-key-map_container {
                width: 100%;
                border-radius: 25px;
                border: 1px solid #880000;
                overflow: hidden
            }

            .st-key-map_container .maplibregl-ctrl-bottom-right {
                display: none !important;
            }

            .st-key-bars_container {
                border-radius: 25px;
                border: 1px solid #880000;
                padding: 20px 60px 20px 60px
            }

            .st-key-bars_container h3 {
                padding-top: 0;
                padding-bottom: 20px;
                margin-top: -8px;
            }

            .st-key-infobox_container {
                border-radius: 25px;
                border: 1px solid #880000;
                padding: 20px 20px
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
                text-align: center
            }

            .st-key-size_container {
                width: 95%;
                border-radius: 25px;
                border: 1px solid #880000;
                height: 150px !important;
                min-height: 150px !important;
                padding: 10px 30px 0px 25px
            }

            </style>
        """, unsafe_allow_html=True
    )