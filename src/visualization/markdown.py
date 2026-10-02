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

            [data-testid="stSidebarContent"] > div {
                padding: 0 !important;
                margin: 0 !important;
            }

            [data-testid="stSidebarHeader"] {
                display: none !important
            }

            /* Divider */
            div[data-testid="stMarkdown"] hr {
                margin-top: 0.25rem;
                margin-bottom: 0.25rem
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

            .st-key-map_container {
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
                padding: 20px 60px
            }

            .st-key-infobox_container {
                border-radius: 25px;
                border: 1px solid #880000;
                padding: 20px 20px
            }

            .st-key-infobox_container div[data-testid="stImage"] {
                height: 30%;
                width: 50%
            }

            .st-key-habitat_container {
                border-radius: 25px;
                border: 1px solid #880000
            }

            </style>
        """, unsafe_allow_html=True
    )